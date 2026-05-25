from django.db import models


# Create your models here.
    

class SimpleUser(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)


    class Meta:
        verbose_name='用户管理'
        verbose_name_plural = '用户管理'


    def __str__(self):
        return self.username
    

class Mushroom(models.Model):
    name = models.CharField(max_length=200, unique=True)
    mycelery = models.BooleanField(default=False)  # 表示是否生成蘑菇