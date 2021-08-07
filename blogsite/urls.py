"""blogsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from web import views
from django.views.static import serve
from blogsite import settings
import os
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('^login/$', views.login, name="login"),
    url('^logout/$', views.logout, name="logout"),
    url('^register/$', views.register, name="register"),
    url('^home/$', views.home, name="home"),
    url('^set/passoword/$', views.set_password, name="set_password"),
    # 编辑器图片上传
    url('^upload/image/$', views.upload_image, name="upload_image"),
    # 资料修改
    url('^userinfo/alter/$', views.userinfo_alter, name="userinfo_alter"),
    url('^get/img_code/$', views.get_img_code, name="get_img_code"),
    # 暴露后端指定文件夹资源
    url('^file/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}, name='file'),
    url('favicon.ico', serve, {'path': 'img/favicon.ico','document_root': os.path.join(settings.BASE_DIR, "static")}),
    # 个人站点
    url('^(?P<username>\w+)/$', views.site, name='site'),
    # 条件筛选
    url('^(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<param>.*)/$', views.site, name='site_screen'),
    # 文章详情，
    url('^(?P<username>\w+)/article/(?P<article_id>\d+)/$', views.article_detail, name='article_detail'),
    # 点赞点踩
    url('^article/up_or_down/$', views.up_down, name='up_down'),
    # 文章删除
    url('^(?P<username>\w+)/manage/article/delete/$', views.article_delete, name='article_delete'),
    # 文章添加
    url('^(?P<username>\w+)/manage/article/add/$', views.article_add, name='article_add'),
    # 文章编辑
    url('^(?P<username>\w+)/manage/article/edit/$', views.article_edit, name='article_edit'),
    # 博客管理
    url('^(?P<username>\w+)/manage/$', views.manage, name='manage'),
    # 标签添加
    url('^(?P<username>\w+)/manage/tag/add/$', views.add_tag, name='add_tag'),
    # 标签删除
    url('^(?P<username>\w+)/manage/tag/delete/$', views.delete_tag, name='delete_tag'),
    # 评论
    url('^(?P<username>\w+)/article/(?P<article_id>\d+)/comment/$', views.comment, name='comment'),
    # 分类添加
    url('^(?P<username>\w+)/manage/category/manage/$', views.add_category, name='add_category'),
    # 分类删除
    url('^(?P<username>\w+)/manage/category/delete/$', views.delete_category, name='delete_category'),
    # 评论删除
    url('^(?P<username>\w+)/manage/comment/delete/$', views.delete_comment, name='delete_comment'),
]
