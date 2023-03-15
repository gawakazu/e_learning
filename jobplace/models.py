from django.db import models
from django.contrib.auth.models import AbstractUser

class TaskModel(models.Model):
    task = models.CharField(max_length=100)
    material_dir = models.CharField(max_length=100)
    already_save = models.CharField(max_length=100)
    def __str__(self):
        return self.task

class ExamModel(models.Model):
    task = models.ForeignKey(TaskModel,on_delete=models.CASCADE)
    question = models.CharField(max_length=100)
    answer = models.CharField(max_length=100)
    def __str__(self):
        return self.question

class MaterialModel(models.Model):
    task = models.ForeignKey(TaskModel,on_delete=models.CASCADE)
    material = models.CharField(max_length=100)
    def __str__(self):
        return self.material

class CustomUser(AbstractUser):
    class Meta(AbstractUser.Meta):
        pass
    belong = models.CharField(max_length=100)
    address = models.CharField(max_length=100,null=True,blank=True)
    zip_code = models.CharField(max_length=100,null=True,blank=True)
    email = models.EmailField(null=True,blank=True)
    age = models.IntegerField(null=True,blank=True)

class RegistorModel(models.Model):
    task = models.ForeignKey(TaskModel,on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    complete_date = models.CharField(max_length=100,null=True,blank=True)
    exam_count = models.CharField(max_length=5000,null=True,blank=True)
    exam_status = models.CharField(max_length=100,null=True,blank=True)
    learn_status = models.CharField(max_length=100,null=True,blank=True)
    def __str__(self):
        return self.complete_date


