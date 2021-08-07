from django import forms
from web import models
from django.core.exceptions import ValidationError


# 基类
class BoostrapForm(object):
    boostrap_exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in self.boostrap_exclude:
                continue
            old_class = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = 'form-control {}'.format(old_class)
            field.widget.attrs['placeholder'] = '请输入%s' % (field.label,)
            field.widget.attrs['autocomplete'] = "off"


class RegisterForm(forms.Form):
    username = forms.CharField(label='用户名', min_length=3, max_length=8, error_messages={
        'required': '用户名不能为空',
        'min_length': '用户名长度必须大于3位',
        'max_length': '用户名长度不能超过8位',
    }, widget=forms.widgets.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='密码', min_length=3, max_length=16, error_messages={
        'required': '密码不能为空',
        'min_length': '密码长度必须大于3位',
        'max_length': '密码长度不能超过16位',
    }, widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(label='确认密码', min_length=3, max_length=16, error_messages={
        'required': '确认密码不能为空',
        'min_length': '确认密码长度必须大于3位',
        'max_length': '确认密码长度不能超过16位',
    }, widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='邮箱', min_length=3, max_length=16, error_messages={
        'required': '邮箱不能为空',
        'invalid': '格式错误',
    }, widget=forms.widgets.EmailInput(attrs={'class': 'form-control'}))

    # 局部钩子：校验用户名是否已存在
    def clean_username(self):
        username = self.cleaned_data.get('username')
        is_exist = models.User.objects.filter(username=username).first()
        if is_exist:
            self.add_error('username', '用户已存在')
        return username

    # 全局钩子：校验两次密码是否一致
    def clean(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if not password == confirm_password:
            self.add_error('confirm_password', '两次密码输入不一致')
        return self.cleaned_data


class UserForm(BoostrapForm, forms.ModelForm):
    class Meta:
        model = models.User
        fields = ['username', 'phone', 'email']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request


class ArticleModelForm(BoostrapForm, forms.ModelForm):
    class Meta:
        model = models.Article
        exclude = ['create_time', 'desc', 'up_num', 'down_num', 'views_num', 'comment_num', 'blog']
        widgets = {
            'category': forms.Select(attrs={'class': 'selectpicker show-tick', }),
            'tag': forms.SelectMultiple(attrs={'class': 'selectpicker show-tick', 'data-actions-box': 'true'}),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

        # 获取当前用户的所有分类
        category_list = [('', '忽略，不选'), ]
        category = models.Category.objects.filter(blog=self.request.user.blog).values_list('id', 'name')
        category_list.extend(category)
        self.fields['category'].choices = category_list

        # 获取当前用户的所有标签
        tag_list = []
        tag = models.Tag.objects.filter(blog=self.request.user.blog).values_list('id', 'name')
        tag_list.extend(tag)
        self.fields['tag'].choices = tag_list


class CommmentModelForm(BoostrapForm, forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ['content', 'parent']

    def clean_parent_id(self):
        parent_id = self.cleaned_data.get('parent_id')
        # reply=models.IssuesReply.objects.filter(id=reply_id).first()
        return parent_id


class TagModelForm(BoostrapForm, forms.ModelForm):
    class Meta:
        model = models.Tag
        fields = ['name']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_name(self):
        name = self.cleaned_data.get('name')
        tag_obj = models.Tag.objects.filter(name=name, blog__user=self.request.user)
        if tag_obj:
            raise ValidationError('标签名已存在')
        return name


class CategoryModelForm(BoostrapForm, forms.ModelForm):
    class Meta:
        model = models.Category
        fields = ['name']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_name(self):
        name = self.cleaned_data.get('name')
        category_obj = models.Category.objects.filter(name=name, blog__user=self.request.user)
        if category_obj:
            raise ValidationError('分类名已存在')
        return name
