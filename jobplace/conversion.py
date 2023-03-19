import csv
import os

def word_conversion(first):
    new = []
    for i in first:
        if int(i)>9 :
            #new.append([int(i)//10])
            #new.append([int(i)%10])
            i = int(i)
            iii = []
            while i > 0:
                remainder = i%10
                i = i//10
                iii.append(remainder)
            iii.reverse()
            new.append(iii)
        else:
            new.append([int(i)])
    return new

def select_conversion(select):
    add_folder = [i.split(',')[0] for i in select] # 20220601 フォルダ名
    task_name = [i.split(',')[1] for i in select] # python
    differ_file = [os.listdir('./static/'+ i) for i in add_folder]
    materials = [[j[:-4] for j in i if j.find('png')>0] for i in differ_file] ### pdfのファイル名 ,python001.pdf->python001
    csv_file = [[j for j in i if j.find('csv')>0] for i in differ_file] ##csv_file csvファイル名　python.csv　拡張子付き
    file_name = []
    for i in range(len(add_folder)):
        file_name.append("./static/" + add_folder[i] + "/" + csv_file[i][0])
    csv_data = []
    for i in file_name:
        csv_file = open(i,"r",encoding="shift-jis")
        reader = csv.reader(csv_file)
        csv_content = []
        for row in reader:
            csv_content.append(row)#print(row)
        csv_data.append(csv_content)
    return add_folder,task_name,materials,csv_data

def task_conversion(already_list,folder_list):
    already_file_list =[i.material_dir for i in already_list]
    add_folder = list(set(folder_list) - set(already_file_list)) #登録さていないフォルダを検出
    differ_file = [os.listdir('./static/'+ i) for i in add_folder]
    #print('--diff--',differ_file)
    #task_name = [i[0][:-4] for i in differ_file]
    task_name = [[j[:-4] for j in i if j.find('csv')>0][0]  for i in differ_file ]
    #print("---task---",task_name)
    return task_name,add_folder

def xy(select):
    select = select.split('_')[1:]
    x = select[1::2]
    try:
        y = [int(i) for i in select[0::2]]
    except:
        y = [int(i) for i in select[0]]
    return x,y
