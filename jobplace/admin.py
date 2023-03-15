from django.contrib import admin
from .models import TaskModel ,ExamModel ,MaterialModel ,CustomUser ,RegistorModel
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

class RegistorModelAdmin(ImportExportModelAdmin):
    list_display = ['id','task','user','complete_date','exam_count','exam_status','learn_status']

class TaskModelAdmin(ImportExportModelAdmin):
    list_display = ['id','task','material_dir','already_save']

class ExamModelAdmin(ImportExportModelAdmin):
    list_display = ['id','task','question','answer']

class MaterialModelAdmin(ImportExportModelAdmin):
    list_display = ['id','task','material']

class CustomUserAdmin(UserAdmin,ImportExportModelAdmin):
    list_display = ['id','username','belong','zip_code','email','age','address']
    empty_value_display = '-empty-'
    fieldsets = (
        (None,{'fields':('username','password')}),
        (_('Personal info'),{'fields':('email','age','belong','zip_code','address')}),
        (_('Permissions'),{'fields':('is_active','is_staff','is_superuser','groups','user_permissions')}),
        (_('Important dates'),{'fields':('last_login','date_joined')}),
    )



admin.site.register(RegistorModel,RegistorModelAdmin)
admin.site.register(TaskModel,TaskModelAdmin)
admin.site.register(ExamModel,ExamModelAdmin)
admin.site.register(MaterialModel,MaterialModelAdmin)
admin.site.register(CustomUser,CustomUserAdmin)