import json
import os
from datetime import datetime

from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from rest_framework import generics


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from .models import SimpleUser
from django.contrib.auth.hashers import check_password

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


import io
from django.db.models import Count
from django.http import HttpResponse


from djangoapp1.big_models.ask_notes import load_ask, analyze_all_files

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

class UserRegister(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            username = serializer.validated_data.get('username')
            # 为新用户创建专属知识库目录
            user_folder = os.path.join(settings.MEDIA_ROOT, 'uploads', username)
            os.makedirs(user_folder, exist_ok=True)
            return Response({'success': True, 'username': username}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogin(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        try:
            user = SimpleUser.objects.get(username=username)
            if check_password(password, user.password):
                # 确保用户目录存在
                user_folder = os.path.join(settings.MEDIA_ROOT, 'uploads', username)
                os.makedirs(user_folder, exist_ok=True)
                return Response({'success': True, 'username': username}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
        except SimpleUser.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# 上传文件

@require_http_methods(["POST"])
def upload_file(request):
    try:
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'code': 400, 'msg': '未获取到文件'}, status=400)

        username = request.POST.get('username', 'default')
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', username)
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, file.name)
        with open(file_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)

        return JsonResponse({
            'code': 200,
            'msg': '上传成功',
            'filename': file.name
        })

    except Exception as e:
        return JsonResponse({'code': 500, 'msg': str(e)}, status=500)


# 发送消息并返回回答

@require_http_methods(["POST"])
def send_message(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        username = data.get('username', 'default')

        if not message:
            return JsonResponse({'code': 400, 'msg': '消息不能为空'}, status=400)

        # 将用户文字输入保存到用户知识库
        user_folder = os.path.join(settings.MEDIA_ROOT, 'uploads', username)
        os.makedirs(user_folder, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        chat_file = os.path.join(user_folder, f'_chat_{timestamp}.txt')
        with open(chat_file, 'w', encoding='utf-8') as f:
            f.write(message)

        reply = load_ask(message, data.get('chartType', ''), folder_path=user_folder)

        return JsonResponse(reply, safe=False)

    except Exception as e:
        return JsonResponse(f"❌ 出错了：{str(e)}", safe=False, status=500)


# 主题关键词分析

@require_http_methods(["POST"])
def analyze_keywords(request):
    try:
        data = json.loads(request.body)
        username = data.get('username', 'default')
        user_folder = os.path.join(settings.MEDIA_ROOT, 'uploads', username)
        result = analyze_all_files(folder_path=user_folder)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'code': 500, 'msg': str(e)}, status=500)
