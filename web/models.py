from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    phone = models.BigIntegerField(null=True, verbose_name='手机号', blank=True)
    avatar = models.FileField(upload_to='avatar/', default='avatar/default.jpg')
    create_time = models.DateField(auto_now_add=True)
    blog = models.OneToOneField(to='BlogSite', null=True,blank=True)

    class Meta:
        verbose_name_plural = '用户表'

    def __str__(self):
        return self.username


class BlogSite(models.Model):
    name = models.CharField(verbose_name='站点名称', max_length=128)
    title = models.CharField(verbose_name='站点标题', max_length=128)
    theme = models.CharField(verbose_name='站点主题', max_length=128)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(verbose_name='文章分类', max_length=128)
    blog = models.ForeignKey(to='BlogSite', null=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(verbose_name='文章标签', max_length=128)
    blog = models.ForeignKey(to='BlogSite', null=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(verbose_name='文章标题', max_length=128)
    desc = models.CharField(verbose_name='文章简介', max_length=256)
    content = models.TextField(verbose_name='文章内容', max_length=128)
    create_time = models.DateField(verbose_name='发布时间', auto_now_add=True)

    up_num = models.IntegerField(verbose_name='点赞数', default=0)
    down_num = models.IntegerField(verbose_name='踩楼数', default=0)
    views_num=models.IntegerField(verbose_name='浏览量', default=0)
    comment_num = models.IntegerField(verbose_name='评论数', default=0)
    blog = models.ForeignKey(to='BlogSite', null=True)
    category = models.ForeignKey(verbose_name="分类",to='Category', null=True, blank=True)
    tag = models.ManyToManyField(verbose_name="标签",to=Tag, through='ArticleToTag', through_fields=('article', 'tag'))

    def __str__(self):
        return self.title


class ArticleToTag(models.Model):
    article = models.ForeignKey(to='Article')
    tag = models.ForeignKey(to='Tag')

    def __str__(self):
        return self.article.title


class UpAndDown(models.Model):
    user = models.ForeignKey(to='User')
    article = models.ForeignKey(to='Article')
    is_up = models.BooleanField()


class Comment(models.Model):
    user = models.ForeignKey(to='User')
    article = models.ForeignKey(to='Article')
    content = models.CharField(max_length=512, verbose_name='评论内容')
    comment_time = models.DateTimeField(verbose_name='评论时间', auto_now_add=True)
    parent = models.ForeignKey(to='self', null=True,blank=True)
