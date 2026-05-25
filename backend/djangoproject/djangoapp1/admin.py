from django.contrib import admin



from .models import SimpleUser


# Register your models here.
admin.site.site_header = '学习笔记图表生成系统后台'
admin.site.site_title= '学习笔记图表生成系统后台'
admin.site.index_title= '学习笔记图表生成系统后台'


admin.site.register(SimpleUser)

