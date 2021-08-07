from django.utils.deprecation import MiddlewareMixin
from web import models
from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings
import datetime


class MiddleWare(MiddlewareMixin):
    def process_request(self, request):
        # 添加白名单，即不用登录也可访问的页面
        '''
        1.获取访问的url
        2.检测url是否在白名单中
        '''
        url = request.path_info
        # if url == '/favicon.ico/':
        #     return
        if url == '/':
            return redirect('/home/')
        if url.split('/')[1] == 'file' and url.split('/')[2] == 'avatar':
            return

        # 在白名单中，返回空，不做其余处理
        if url in settings.WHITE_REGES_URL_LIST:
            # print('白名单',url)
            return
        # 不在名单中，返回登录页面
        else:
            # print('黑名单',url)
            if request.user.is_authenticated():
                return
            else:
                try:
                    if url.split('/')[2] == 'article' and (url.split('/')[3]).isdigit() == True:
                        obj = models.Article.objects.filter(id=int(url.split('/')[3])).first()
                        if  obj:
                            return
                        else:
                            return render(request, '404.html')
                except Exception as e:
                    return redirect('/login/')

