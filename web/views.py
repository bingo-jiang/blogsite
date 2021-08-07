from django.shortcuts import render, redirect
from django.contrib import auth
from web.myforms import RegisterForm, ArticleModelForm, CommmentModelForm, TagModelForm, CategoryModelForm,UserForm
from django.http import JsonResponse
from web import models
from scripts.pic_code import check_code
from django.shortcuts import HttpResponse
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from scripts.filename_format import filename_format
from django.db.models import Count, functions
from django.urls import reverse
from scripts import pagination
import os
from blogsite import settings
from bs4 import BeautifulSoup
from django.db.models import Q


# Create your views here.
# 使用auth模块对用户相关操作进行校验
# 注意：要用auth模块，就用全套
@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        # 校验验证码
        if code.upper() == request.session.get('img_code').upper():
            # 去用户表进行校验，用户名和密码(但是密码是密文的）
            # 使用auth进行校验(需要同时传入账号密码）,它会返回一个user对象
            user_obj = auth.authenticate(request, username=username, password=password)
            # 校验后进行登录状态的保存
            if user_obj:
                request.session.set_expiry(60 * 60 * 24 * 30)
                auth.login(request, user_obj)  # 相当于request.session[]=user_obj
                return JsonResponse({'status': True, 'data': '/home/'})
            else:
                return JsonResponse({'status': False, 'error': '用户名或密码错误'})
        else:
            return JsonResponse({'status': False, 'error': '验证码错误'})
    else:
        return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # 将user表中没有的字段剔除
            data.pop('confirm_password')
            # 获取头像对象
            file_obj = request.FILES.get('avatar', None)
            if file_obj:
                file_obj.name = filename_format(request.POST.get('username'), file_obj.name)
                data['avatar'] = file_obj
                # print(data)
            models.User.objects.create_user(**data)
            return JsonResponse({'status': True, 'data': '/login/'})
        else:
            return JsonResponse({'status': False, 'error': form.errors})
        # return JsonResponse({'status': False, 'error': '测试'})
    else:
        form = RegisterForm()
        res = {
            'form': form
        }
        return render(request, 'register.html', res)


# @login_required
def home(request):
    # 判断用户是否登录request.user.is_authenticated()
    keyword = request.GET.get('keyword')
    article_obj = models.Article.objects.all().order_by('-create_time', '-id')
    hot_article_obj = models.Article.objects.order_by('-views_num', 'up_num', 'id')[0:10]
    recommend_article_obj = models.Article.objects.order_by('-up_num', 'down_num', 'id')[0:10]
    for i in article_obj:
        id=i.id
        content=i.content
        soup = BeautifulSoup(content, 'html.parser')
        desc = soup.text[0:256]
        models.Article.objects.filter(id=id).update(desc=desc)
    if keyword:
        obj_list = models.Article.objects.filter(
            Q(title__icontains=keyword) | Q(content__icontains=keyword)
        )
        article_obj = obj_list
    # 分页器
    queryset = article_obj
    page_object = pagination.Pagination(
        current_page=request.GET.get('page'),
        all_count=queryset.count(),
        base_url=request.path_info,
        query_params=request.GET
    )
    object_list = queryset[page_object.start:page_object.end]
    res = {
        'article_obj': article_obj,
        'hot_article_obj': hot_article_obj,
        'recommend_article_obj': recommend_article_obj,
        'object_list': object_list,
        'page_html': page_object.page_html(),
    }
    if request.user.is_authenticated():
        userform = UserForm(request, instance=request.user)
        res['userform']=userform
    return render(request, 'home.html', res)


@csrf_exempt
@login_required
def set_password(request):
    old_pwd = request.POST.get('old_password')
    new_pwd = request.POST.get('new_password')
    confirm_pwd = request.POST.get('confirm_password')
    # print(request.POST)
    # 校验旧密码
    check_old = request.user.check_password(old_pwd)
    if check_old:
        # 校验两次密码是否一致
        if new_pwd == confirm_pwd:
            request.user.set_password(new_pwd)
            request.user.save()
            return JsonResponse({'status': True, 'data': '/login/'})
        else:
            return JsonResponse({'status': False, 'confirm_error': '两次密码输入不一致'})
    else:
        return JsonResponse({'status': False, 'error': '原密码错误'})


@login_required
def logout(request):
    auth.logout(request)
    return redirect('login')


# 图片验证码
def get_img_code(request):
    img_obj, code = check_code()
    # 设置session
    request.session['img_code'] = code
    request.session.set_expiry(300)
    # 存入内存中
    stream = BytesIO()
    img_obj.save(stream, 'png')
    return HttpResponse(stream.getvalue())


# 资料修改
@csrf_exempt
def userinfo_alter(request):
    res={'status':True,'error':None,'data':None}
    if request.method == 'POST':
        user_obj=request.user
        form = UserForm(request=request,data=request.POST,instance=user_obj)
        if form.is_valid():
            file_obj = request.FILES.get('avatar')
            if file_obj:
                file_obj.name = filename_format(request.POST.get('username'), file_obj.name)
                print(file_obj.name)
                form.instance.avatar = file_obj
            form.save()
        else:
            res['status']=False
            res['error']=form.errors
    return JsonResponse(res)

# 编辑器图片上传接口
@csrf_exempt
def upload_image(request):
    res = {}
    if request.method == 'POST':
        file_obj = request.FILES.get('imgFile')
        file_obj.name = filename_format(request.user.username, file_obj.name)
        print(file_obj.name)
        # 手动拼接存储文件的路径
        file_dir = os.path.join(settings.BASE_DIR, 'file', 'article_img')
        # 优化操作
        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)
        # 拼接完整路径
        file_path = os.path.join(file_dir, file_obj.name)
        print(file_path)
        try:
            with open(file_path, 'wb') as f:
                for line in file_obj:
                    f.write(line)
        except Exception as e:
            print(e)
            return JsonResponse({'err':e})
        res['url'] = "/file/article_img/{}".format(file_obj.name)
        return JsonResponse(res)
    return JsonResponse({"error": 0, })


# 个人站点
def site(request, username, **kwargs):
    '''
    :param request:
    :param username: 个人博客的博客站点名称
    :param kwargs: 如果该参数有值，就是增加文章表的过滤条件
    :return:
    '''
    keyword = request.GET.get('keyword')
    user_obj = models.User.objects.filter(username=username).first()
    if not user_obj:
        return render(request, '404.html')
    else:
        # 查询该用户下的所有文章
        blog = user_obj.blog
        article_obj = models.Article.objects.filter(blog=blog).all()
        if kwargs:
            condition = kwargs.get('condition')
            param = kwargs.get('param')
            if condition == 'category':
                article_obj = article_obj.filter(category_id=param)
            elif condition == 'tag':
                article_obj = article_obj.filter(tag__id=param)
            else:
                year, month = param.split('-')
                article_obj = article_obj.filter(create_time__year=year, create_time__month=month)
        # # 查询各分类下的文章及文章数
        # category_obj = models.Category.objects.filter(blog=blog).annotate(
        #     count_num=Count('article')
        # ).values_list('name', 'count_num', 'pk')
        # # 查询各标签下的文章及文章数
        # tag_obj = models.Tag.objects.filter(blog=blog).annotate(
        #     count_num=Count('article')
        # ).values_list('name', 'count_num', 'pk')
        # # 查询各日期下的文章及文章数
        # sort_by_month_obj = models.Article.objects.filter(blog=blog).annotate(
        #     month=functions.TruncMonth('create_time')).values_list('month').annotate(
        #     num=Count('id')).values_list('month', 'num')
        if keyword:
            obj_list = models.Article.objects.filter(
                Q(title__icontains=keyword) | Q(content__icontains=keyword)
            )
            article_obj = obj_list
        queryset = article_obj
        page_object = pagination.Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),
            base_url=request.path_info,
            query_params=request.GET
        )
        object_list = queryset[page_object.start:page_object.end]
        res = {
            'user_obj': user_obj,
            'article_obj': article_obj,
            'object_list': object_list,
            'page_html': page_object.page_html(),
            # 'category_obj': category_obj,
            # 'tag_obj': tag_obj,
            # 'sort_by_month_obj': sort_by_month_obj,
        }
        if request.user.is_authenticated():
            userform = UserForm(request, instance=request.user)
            res['userform'] = userform
        return render(request, 'own_blog.html', res)



def article_detail(request, username, article_id):
    comment = request.GET.get('comment')  # 通过该参数判断是否跳到评论下
    user_obj = models.User.objects.filter(username=username).first()
    if not user_obj:
        return render(request, '404.html')
    else:
        # 查询该用户下的所有文章
        blog = user_obj.blog
    article_obj = models.Article.objects.filter(pk=article_id, blog__user=user_obj).first()
    old_views_num = int(article_obj.views_num)
    # print(old_views_num)
    models.Article.objects.filter(pk=article_id, blog__user=user_obj).update(views_num=old_views_num + 1)

    tag_obj = models.ArticleToTag.objects.filter(article_id=article_id).all()
    if not article_obj:
        return render(request, '404.html')
    res = {
        'user_obj': user_obj,
        'blog': blog,
        'article_obj': article_obj,
        'tag_obj': tag_obj,
        'comment': comment,
        'username':username,
    }
    if request.user.is_authenticated():
        userform = UserForm(request, instance=request.user)
        res['userform']=userform
    return render(request, 'article_detail.html', res)


# 文章赞或踩
# @login_required
@csrf_exempt
def up_down(request):
    if not request.user.is_authenticated():
        return JsonResponse({'status': True, 'login': True,'url':'/login/'})
    article_id = request.POST.get('article_id')
    up = int(request.POST.get('up'))
    # print('是否为',article_id,'点赞',up)
    article_obj = models.Article.objects.filter(id=article_id).first()
    up_down_obj = models.UpAndDown.objects.filter(article_id=article_id, user=request.user).first()
    res = {'status': True, 'error': None}
    if not article_obj:
        res['status'] = False
        res['error'] = "没有此文章!"
        return JsonResponse(res)
    if up_down_obj:
        res['status'] = False
        res['error'] = "已赞或已踩!"
        return JsonResponse(res)
    if up == 1:
        old_up_num = int(article_obj.up_num)
        models.Article.objects.filter(id=article_id).update(up_num=old_up_num + 1)
        # article_obj.update()
        models.UpAndDown.objects.create(user=request.user, article_id=article_id, is_up=True)
        return JsonResponse(res)
    else:
        old_down_num = int(article_obj.down_num)
        article_obj.update(down_num=old_down_num + 1)
        models.UpAndDown.objects.create(user=request.user, article_id=article_id, is_up=False)
        return JsonResponse(res)


@login_required
def manage(request, username):
    keyword = request.GET.get('keyword')
    form = TagModelForm(request)
    category_form = CategoryModelForm(request=request)
    user_obj = models.User.objects.filter(username=username).first()
    if not user_obj:
        return render(request, '404.html')
    article_obj = models.Article.objects.filter(blog__user=request.user).all().order_by('-create_time', '-id')
    comment_obj = models.Comment.objects.filter(user=request.user).all()
    tag_obj = models.Tag.objects.filter(blog__user=request.user).all()
    if keyword:
        obj_list = models.Article.objects.filter(
            Q(title__icontains=keyword) | Q(content__icontains=keyword)
        )
        article_obj = obj_list
    # 文章分页器
    queryset = article_obj
    page_object = pagination.Pagination(
        current_page=request.GET.get('page'),
        all_count=queryset.count(),
        base_url=request.path_info,
        query_params=request.GET,
        per_page=10,
    )
    object_list = queryset[page_object.start:page_object.end]

    # 标签分页器
    tag_page_object = pagination.MyPagination(
        current_page=request.GET.get('page'),
        all_count=tag_obj.count(),
        base_url=request.path_info,
        query_params=request.GET,
        browser_param='tags',
        per_page=10,
    )
    tag_object_list = tag_obj[tag_page_object.start:tag_page_object.end]
    # 评论分页器
    comment_page_object = pagination.MyPagination(
        current_page=request.GET.get('page'),
        all_count=comment_obj.count(),
        base_url=request.path_info,
        query_params=request.GET,
        browser_param='comments',
        per_page=10,
    )
    comment_object_list = comment_obj[comment_page_object.start:comment_page_object.end]
    category_obj = models.Category.objects.filter(blog__user=request.user).all()
    res = {
        'user_obj': user_obj,
        'object_list': object_list,
        'page_html': page_object.page_html(),
        'form': form,
        'category_form': category_form,
        'tag_object_list': tag_object_list,
        'tag_page_html': tag_page_object.page_html(),
        'comment_object_list': comment_object_list,
        'comment_page_html': comment_page_object.page_html(),
        'category_obj': category_obj,
    }
    if request.user.is_authenticated():
        userform = UserForm(request, instance=request.user)
        res['userform']=userform
    return render(request, 'manage.html', res)


@login_required
def article_delete(request, username):
    res = {'status': True, 'data': None, 'error': None}
    id = request.GET.get('Aid')
    article_obj = models.Article.objects.filter(id=id, blog__user=request.user)
    if request.user.username != username:
        res['status'] = False
        res['error'] = "非博客主，不能进行此操作！"
        return JsonResponse(res)
    if not article_obj:
        res['status'] = False
        res['error'] = "非法访问，非法操作！"
        return JsonResponse(res)
    article_obj.delete()
    return JsonResponse(res)


@csrf_exempt
def article_add(request, username):
    user_obj = request.user
    form = ArticleModelForm(request=request)
    res = {
        'form': form,
        'user_obj': user_obj
    }
    if request.method == "GET":
        if request.user.is_authenticated():
            userform = UserForm(request, instance=request.user)
            res['userform'] = userform
        return render(request, 'article_add.html', res)
    else:
        result = {'status': True, 'data': "", 'error': None}
        title = request.POST.get('title')
        content = request.POST.get('content')
        category = request.POST.get('category')
        tag = request.POST.getlist('tag')
        soup = BeautifulSoup(content, 'html.parser')
        desc=soup.text[0:256]
        tags = soup.find_all()
        for html in tags:
            if html.name == 'script':
                # 删除标签
                html.decompose()
        if not title or not content:
            result['status'] = False
            result['error'] = "标题或内容不能为空"
            return JsonResponse(result)
        if not tag:
            result['status'] = False
            result['error'] = "标签不能为空"
            return JsonResponse(result)
        article_obj = models.Article.objects.create(
            title=title,
            desc=desc,
            content=str(soup),
            category_id=category,
            blog=request.user.blog,
        )
        article_obj_list = []
        for i in tag:
            to_tag_obj = models.ArticleToTag(article=article_obj, tag_id=i)
            article_obj_list.append(to_tag_obj)
        models.ArticleToTag.objects.bulk_create(article_obj_list)
        url = reverse('manage', kwargs={'username': request.user.username})
        result['data'] = url
        return JsonResponse(result)


def article_edit(request, username):
    if request.method == 'GET':
        article_id = request.GET.get('article_id')
        article_obj = models.Article.objects.filter(id=article_id).first()
        if not article_obj:
            return render(request, '404.html')
        user_obj = request.user
        form = ArticleModelForm(request=request, instance=article_obj)
        res = {
            'form': form,
            'user_obj': user_obj,
            'article_id': article_id,
        }
        if request.user.is_authenticated():
            userform = UserForm(request, instance=request.user)
            res['userform'] = userform
        return render(request, 'article_edit.html', res)
    else:
        result = {'status': True, 'data': "", 'error': None}
        article_id = request.POST.get('article_id')
        title = request.POST.get('title')
        content = request.POST.get('content')
        category = request.POST.get('category')
        tag = request.POST.getlist('tag')
        if not title or not content:
            result['status'] = False
            result['error'] = "标题或内容不能为空"
            return JsonResponse(result)
        if not tag:
            result['status'] = False
            result['error'] = "标签不能为空"
            return JsonResponse(result)
        article_obj = models.Article.objects.filter(id=article_id, blog=request.user.blog)
        if not article_obj:
            result['status'] = False
            result['error'] = "非文章作者，无法操作!"
            return JsonResponse(result)
        article_obj.update(
            title=title,
            desc=content[0:128],
            content=content,
            category_id=category,
            blog=request.user.blog,
        )
        models.ArticleToTag.objects.filter(article_id=article_id).delete()
        article_obj_list = []
        for i in tag:
            to_tag_obj = models.ArticleToTag(article_id=article_id, tag_id=i)
            article_obj_list.append(to_tag_obj)
        models.ArticleToTag.objects.bulk_create(article_obj_list)
        url = reverse('article_detail', kwargs={'username': request.user.username, 'article_id': article_id})
        result['data'] = url
        return JsonResponse(result)


@csrf_exempt
def comment(request, username, article_id):
    if request.method == 'GET':
        comment_list = models.Comment.objects.filter(article_id=article_id)
        num = 0
        # 将reply原queryset类型转为json格式
        data_list = []
        for row in comment_list:
            num += 1
            data = {
                'num': '#' + str(num) + '楼',
                'id': row.id,
                'content': row.content,
                'creator': row.user.username,
                'create_datetime': row.comment_time.strftime('%Y-%m-%d %H:%M:%S'),
                'parent_id': row.parent_id,
            }
            data_list.append(data)
        return JsonResponse({'status': True, 'data': data_list})
    # POST请求
    else:
        form = CommmentModelForm(data=request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.instance.article_id = article_id
            comment_obj = models.Comment.objects.filter(article_id=article_id)
            num = comment_obj.count() + 1
            row = form.save()
            obj = models.Article.objects.filter(id=article_id)
            old_comment_num = obj.first().comment_num
            obj.update(comment_num=old_comment_num + 1)
            info = {
                'num': '#' + str(num) + '楼',
                'id': row.id,
                'content': row.content,
                'creator': row.user.username,
                'create_datetime': row.comment_time.strftime('%Y-%m-%d %H:%M:%S'),
                'parent_id': row.parent_id,
            }
            return JsonResponse({'status': True, 'data': info})
        else:
            return JsonResponse({'status': False, 'error': form.errors})


def add_tag(request, username):
    manage_type = request.POST.get('type')
    res = {'status': True, 'error': None}
    if request.user.username != username:
        res['status'] = False
        res['error'] = '非博客主，不能进行此操作!'
        return JsonResponse(res)
    else:
        url = request.path_info + '?' + request.GET.urlencode()
        url = url + '#tags'
        if manage_type == 'add':
            form = TagModelForm(data=request.POST,request=request)
            if form.is_valid():
                form.instance.blog = request.user.blog
                form.save()
                res['data'] = url
                return JsonResponse(res)
            else:
                return JsonResponse({'status': False, 'form_error': form.errors})
        if manage_type == 'edit':
            tag_id = request.POST.get('id')
            tag_obj = models.Tag.objects.filter(id=tag_id, blog=request.user.blog).first()
            if not tag_obj:
                res['status'] = False
                res['error'] = '没有该标签!'
                return JsonResponse(res)
            form = TagModelForm(request,data=request.POST, instance=tag_obj)
            if form.is_valid():
                form.save()
                res['data'] = url
                return JsonResponse(res)
            else:
                return JsonResponse({'status': False, 'form_errors': form.errors})


def delete_tag(request, username):
    res = {'status': True, 'data': None, 'error': None}
    id = request.GET.get('Aid')
    tag_obj = models.Tag.objects.filter(id=id, blog__user=request.user)
    if request.user.username != username:
        res['status'] = False
        res['error'] = "非博客主，不能进行此操作！"
        return JsonResponse(res)
    if not tag_obj:
        res['status'] = False
        res['error'] = "非法访问，非法操作！"
        return JsonResponse(res)
    tag_obj.delete()
    url = request.path_info + '?' + request.GET.urlencode()
    url = url + '#tags'
    res['data'] = url
    return JsonResponse(res)


def add_category(request, username):
    manage_type = request.POST.get('type')
    url = reverse('manage', kwargs={'username': request.user.username})
    res = {'status': True, 'error': None}
    if request.user.username != username:
        res['status'] = False
        res['error'] = '非博客主，不能进行此操作!'
        return JsonResponse(res)
    else:
        if manage_type == 'add':
            form = CategoryModelForm(data=request.POST,request=request)
            print(request.POST)
            if form.is_valid():
                form.instance.blog = request.user.blog
                form.save()
                res['data'] = url
                return JsonResponse(res)
            else:
                print(form.errors)
                return JsonResponse({'status': False, 'form_error': form.errors})
        if manage_type == 'edit':
            category_id = request.POST.get('id')
            category_obj = models.Category.objects.filter(id=category_id, blog=request.user.blog).first()
            if not category_obj:
                res['status'] = False
                res['error'] = '没有该分类!'
                return JsonResponse(res)
            form = CategoryModelForm(data=request.POST, instance=category_obj,request=request)
            if form.is_valid():
                form.save()
                res['data'] = url
                return JsonResponse(res)
            else:
                return JsonResponse({'status': False, 'error1': form.errors.get('name')})
        res['status'] = False
        res['error'] = '请求类型错误!'
        return JsonResponse(res)


def delete_category(request, username):
    res = {'status': True, 'data': None, 'error': None}
    id = request.GET.get('Aid')
    category_obj = models.Category.objects.filter(id=id, blog__user=request.user)
    if request.user.username != username:
        res['status'] = False
        res['error'] = "非博客主，不能进行此操作！"
        return JsonResponse(res)
    if not category_obj:
        res['status'] = False
        res['error'] = "非法访问，非法操作！"
        return JsonResponse(res)
    category_obj.delete()
    url = request.path_info + '?' + request.GET
    res['data'] = url
    return JsonResponse(res)


def delete_comment(request, username):
    res = {'status': True, 'data': None, 'error': None}
    id = request.GET.get('Aid')
    comment_obj = models.Comment.objects.filter(id=id, user=request.user)
    if request.user.username != username:
        res['status'] = False
        res['error'] = "非博客主，不能进行此操作！"
        return JsonResponse(res)
    if not comment_obj:
        res['status'] = False
        res['error'] = "非法访问，非法操作！"
        return JsonResponse(res)
    comment_obj.delete()
    url = request.path_info + '?' + request.GET
    url = url + '#comments'
    res['data'] = url
    return JsonResponse(res)
