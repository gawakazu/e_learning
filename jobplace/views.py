from django.shortcuts import render,redirect
from django.views.generic import ListView,DetailView,TemplateView,View
from django.contrib.auth import login,logout,authenticate,views as auth_views
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from .models import TaskModel,ExamModel,MaterialModel,RegistorModel,CustomUser
from .forms import LoginForm
import datetime
import os
from . import models ,graph ,conversion


class LoginView(auth_views.LoginView):
    template_name = 'login.html'
    form_class = LoginForm

class LogoutView(LoginRequiredMixin,LogoutView):
    template_name = 'logout.html'

### ユーザーに割り当てられた未完了なタスクを表示する。
class MainView(LoginRequiredMixin,ListView):
    template_name = 'main.html'
    model = RegistorModel
    def get_queryset(self):
        queryset = super().get_queryset()
        # 未完了は、complate_date=0。
        queryset = queryset.filter(user=self.request.user,complete_date=0)
        return queryset
    
### Mainで選択したタスクの学習資料を一覧表示する。　学習済を表示する(task.htmlで☒表示、未は□)。　学習完了後、テストの実施を可能とする。
class TaskView(LoginRequiredMixin,TemplateView):
    template_name = 'task.html'
    model = RegistorModel
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        # try:mainから移動。 main.htmlで選択されたregistorのi(pk)よりﾀｽｸを特定（a,b行）し、MaterialModelにﾀｽｸを代入して学習資料(materialのPDF)を取得(c行)。･･･➀
        # except:materialから移動。material.htmlでmaterial(pdf名)より、移動元を学習完了として順番(material_number)を抽出(f行)しlearn_statusを2に(d行)する。➀も行う(a-->e行)。
        try: 
            id = self.kwargs['pk'] 
            registor_queryset = RegistorModel.objects.filter(id=id) # a
        except: 
            material = self.kwargs['material'] 
            # self.kwargs['material']=python001　、material_number = int(material[-1:])=1　、self.kwargs['material'][:-3]=python
            material_number = int(material[-1:]) # f
            registor = RegistorModel.objects.get(user=self.request.user,task__task=self.kwargs['material'][:-3]) 
            registor.learn_status = registor.learn_status[0:material_number-1] + "2" + registor.learn_status[material_number:] # d
            registor.save()        
            registor_queryset = RegistorModel.objects.filter(user=self.request.user,task__task=self.kwargs['material'][:-3]) # e
        data = [[i.task,i.learn_status] for i in registor_queryset][0] # b
        # data_list:MaterialModelの学習資料(pdfﾌｧｲﾙ名)と、学習の進捗(learn_status)。Learn_status：1は未完、2は完了。task.htmlで1なしでﾃｽﾄﾎﾞﾀﾝ表示。
        data_list = zip(MaterialModel.objects.filter(task=data[0]),list(str(data[1]))) # c
        # lraern_statusはﾃｽﾄﾎﾞﾀﾝ表示の判定のために別途作成。
        learn_status = str(data[1])
        task = data[0]
        context['data_list'] = data_list
        context['learn_status'] = learn_status
        context['task'] = task
        return context

### 選択されたタスクの学習資料を表示する。 資料のPDFの取得を可能とする。
class MaterialView(LoginRequiredMixin,TemplateView):
    template_name = 'material.html'
    model = RegistorModel
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        # iは、task.html/data_list/i。　つまり、MaterialModel.objects.filter(task=data[0])　で「python001」(c行)。
        material = self.kwargs['i']
        # task[:-3]で　python001 --> python を抽出。
        task_queryset = TaskModel.objects.filter(task=material[:-3]) 
        # staticには登録日のフォルダを作成し保存（例:20220601)。　20220601はTaskModelのmaterial_dirとして保存。
        # TaskViewのalready_saveは読込んだﾀｽｸを1で表示。現在、未使用。
        directory = '/static/' + [[i.material_dir] for i in task_queryset][0][0] +'/'+ material + ".png"
        context['directory'] = directory
        context['material'] = material
        return context

### タスクに割り当てられた試験を、実施する。　問題により1つ、または、複数の回答を選択する。 
class ExamView(LoginRequiredMixin,TemplateView):
    template_name = 'exam.html'
    model =ExamModel
    def get_context_data(self,**kwargs):
        context= super().get_context_data(**kwargs)
        # 'task'は、TaskViewのcontext['task']　RegistorModelのtaskで、python。
        exam_queryset = ExamModel.objects.filter(task__task=self.kwargs['task']) 
        registor = RegistorModel.objects.get(task__task=self.kwargs['task'],user=self.request.user)
        # exam_statusは、1ケタはradioボタン、2桁はcheckボタン。9は未回答、9以外は選択した番号。
        exam_status = registor.exam_status.split("/")
        # question_numは、未回答の問題の番号。questions_and_choices[question_num]で、未回答の問題のリストを作成
        question_num = exam_status.index("9") 
        questions_and_choices = [i.question.split('/') for i in exam_queryset]
        #　問題文に、問題の全数と現在何問目かを、分数で表示。　[第1/3問]を問題文に追加。
        for i in range(len(questions_and_choices)):
            questions_and_choices[i][0] = "第[" + str(i+1) +'/' + str(len(questions_and_choices)) + "]問： " + questions_and_choices[i][0]
        # answerは、問題の正解。複数選択問題では、2桁。
        answer = [int(i.answer) for i in exam_queryset][question_num]
        question_and_choice = questions_and_choices[question_num]
        print('-----',question_and_choice)
        context['question_and_choice'] = question_and_choice
        context['answer'] = answer
        print('---question_and_choice---',question_and_choice)
        return context
    def post(self,request,task,**kwargs):
        # choiceは、exam.htmlのradio、または、checkboxの選択番号
        try:
            choice = request.POST.getlist('choice')
            # 選択されていない場合、元に戻る。
            if choice[0] == "":
                return redirect('exam',task)
            # choice:問題文が1となるため、選択した回答から-1を行う。
            choice = [int(i)-1 for i in choice]
            # all_choices:複数選択問題の回答をマージする。choice:[1,3,4]-->all_choices:134
            all_choices = ''.join(map(str,choice)) 
            # 'task'は、TaskViewのcontext['task']　RegistorModelのtaskで、python。
            registor = RegistorModel.objects.get(task__task=task,user=self.request.user)
            # exam_status= 2/9/ -> 2　番目　(/も含めて、0からｶｳﾝﾄ)
            str_question_num = registor.exam_status.find('9') 
            # 回答した番号を9から書換える。
            registor.exam_status = registor.exam_status[0:str_question_num] + str(all_choices) + registor.exam_status[str_question_num + 1:]
            registor.save()
            # 9/が存在しない場合は、問題への回答が完了と判断し、resultへ移動。
            if registor.exam_status.find('9/') == -1:
                return redirect('result',task)
            return redirect('exam',task)
            #return render(request,'exam.html',{'question_and_choice':['第[2/200]問： 散歩は1日何回必要ですか?', '1回。', '特に何もする必要はない。', '3回']})
        except:
            return redirect('exam',task)

### テストの結果を、問題毎に正解、回答を一覧にして表示する。
class ResultView(LoginRequiredMixin,TemplateView):
    template_name = 'result.html'
    def get_context_data(self,task,**kwargs):
        context = super().get_context_data(**kwargs)
        exam_queryset = ExamModel.objects.filter(task__task=task)
        # 問題のリスト
        questions =[i.question.split('/') for i in exam_queryset]
        # 問題の「正解(答え)」のリスト
        answers = [int(i.answer) for i in exam_queryset]
        # 9以上の複数選択問題の「答え」を分解する
        all_answers = conversion.word_conversion(answers) 
        registor = RegistorModel.objects.get(task__task=task,user=self.request.user)
        # 問題の「回答」のリスト　int_exam_statusは、str-->intへ。
        exam_status = (registor.exam_status).split('/')[:-1]
        int_exam_status = [int(i) for i in exam_status]    
        # 9以上の複数選択問題の「回答」を分解する
        all_exam_status = conversion.word_conversion(exam_status) 
        question_answer_choice = zip(questions,all_answers,all_exam_status)
        context['question_answer_choice'] = question_answer_choice
        # 正解と回答が異なる場合、Fail。
        if all_answers != all_exam_status:
            result = '-------【Fail】-------'
            # 不正解な問題を抽出。　差集合(set(answers)-set(int_exam_status))
            ng_question = list(set(answers)-set(int_exam_status))
            # 問題の正解数を取得。 正解数 = 全数 - 不正解数
            correct_count = len(answers) - len(ng_question)
            registor = RegistorModel.objects.get(task__task=task,user=self.request.user)
            question_count = len(answers)
            # 初期値9に再設定。　問題数2なら、9/9/に初期化。
            registor.exam_status = "9/" * question_count 
            # exam_countに、本試験の正解数と日付を追加。正解数/日付/ --> /1/2023-02-18/
            registor.exam_count += str(correct_count) + '/' + str(datetime.date.today()) +'/' 
            registor.save()
        else:
            result = '-------【Pass】-------'
            registor = RegistorModel.objects.get(task__task=task,user=self.request.user)
            # complete_dateに、本日の日付を記載。
            registor.complete_date = datetime.date.today()
            registor.exam_count += str(len(answers)) + '/' + str(datetime.date.today()) 
            registor.save()
        context['result'] = result
        return context

### 管理者向け　ルールに基づくﾌｫﾙﾀﾞのデータより、指定のユーザーにタスクを追加する。
class KanriView(UserPassesTestMixin,TemplateView):
    template_name = 'kanri.html'
    def test_func(self):
        #return self.request.user.belong == "a"
        return self.request.user.is_staff
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        # "."が無いことで、フォルダを抽出。　つまり、detail.cssは抽出せず。
        folder_list = [i for i in os.listdir('./static') if i.find('.')==-1]
        # task_queryset:登録済タスク、foloder_list:全てのフォルダ
        task_queryset = TaskModel.objects.all()
        # add_folder：未登録フォルダ　、task_name：csvファイル名より抽出(python.csv --> python)　csvﾌｧｲﾙはﾌｫﾙﾀﾞ内の［0］のﾌｧｲﾙ。
        task_name,add_folder = conversion.task_conversion(task_queryset,folder_list) 
        add_folder = zip(add_folder,task_name)
        context['add_folder'] = add_folder
        return context
    def post(self,request,*args,**kwargs):
        context = super().get_context_data(**kwargs)
        # ﾌｫﾙﾀﾞ名とﾀｽｸ名 kanri.htmlのinputﾀｸﾞのvalue ="{{i}},{{j}}"　　i,jは、{% for i,j in add_folder %}
        select = request.POST.getlist('select')
        # add_folder:ﾌｫﾙﾀﾞ名　,task_name:ﾀｽｸ名(python),　materials：ﾃｷｽﾄ名(python001,python002),　csv_data：問題
        add_folder,task_name,materials,csv_data = conversion.select_conversion(select) 
        # 複数選択を考慮し、task_nameの長さでﾙｰﾌﾟ。
        for i in range(len(task_name)):
            TaskModel(task=task_name[i],material_dir=add_folder[i],already_save=1).save()
            task = TaskModel.objects.get(task=task_name[i])   
            # materials（資料）の数だけ、modelを作成。        
            for j in materials[i]:
                MaterialModel.objects.create(task=task,material=j)
            # 問題の数だけ、ExamModelを作成。
            for k in range(1,len(csv_data[i])):
                question = csv_data[i][k][0:1] + csv_data[i][k][2:]
                str_question = '/'.join(question)
                if str_question[-1] =='/':
                     str_question = str_question[:-1]
                answer = csv_data[i][k][1:2]
                ExamModel.objects.create(task=task,question=str_question,answer=answer[0])
            # 割り当てたﾕｰｻﾞ毎にRegistorModelを作成。　学習中、学習完了後のﾃﾞｰﾀを管理。
            for m in csv_data[i][0][0]:
                customuser = CustomUser.objects.filter(belong=m)
                usernames = [i.username for i in customuser]
                for username in usernames:
                    #csv_data[i]-1は、i番目の問題の数。-1は1行目のbelong分を引いている。exam_statusは試験状況、learn_statusは学習状況。
                    exam_status = '9/' * (len(csv_data[i])-1) 
                    learn_status = '1' * (len(materials[i])) 
                    user_name = CustomUser.objects.get(username=username)
                    RegistorModel.objects.create(task=task,user=user_name,complete_date=0,exam_count='/',exam_status=exam_status,learn_status=learn_status)
        return redirect('main')

### 完了済のタスクの試験の経過を確認する。
class InformationView(LoginRequiredMixin,TemplateView):
    template_name = 'information.html'
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        registor_queryset = RegistorModel.objects.filter(user=self.request.user).exclude(complete_date=0)
        complete_data = [[i.task,i.exam_count] for i in registor_queryset]
        context['complete_data'] = complete_data
        return context
    def post(self,request,*args,**kwargs):
        try:
            select = request.POST['select']
        except:
            return redirect("information")
        select = str(select.split(',')[1])
        select = select.replace('/','_')
        return redirect('index',select)

### 試験結果の推移を図で表示する。
class IndexView(LoginRequiredMixin,TemplateView):
    template_name = 'index.html'
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        select = self.kwargs['select']
        x,y = conversion.xy(select)
        chart = graph.Plot_Graph(x,y)
        context['chart'] = chart
        return context