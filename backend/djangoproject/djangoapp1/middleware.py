from django.utils.deprecation import MiddlewareMixin
import json

class CloseCsrfMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.csrf_processing_done = True

class MD_request(MiddlewareMixin):
    # 请求中间件
    def process_request(self, request):
        if request.method != 'GET' and request.META.get('CONTENT_TYPE') == 'application/json':
            data = json.loads(request.body)
            request.data = data
 
# 响应中间件
    def process_response(self, request, response):
        return response