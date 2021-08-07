from django import template
from web import models
from django.db.models import Count, functions

register = template.Library()


@register.inclusion_tag('tags/left_menu.html')
def left_menu(username):
    # 构造侧边栏的数据
    user_obj = models.User.objects.filter(username=username).first()
    if user_obj:
        blog = user_obj.blog
        # 查询各分类下的文章及文章数
        category_obj = models.Category.objects.filter(blog=blog).annotate(
            count_num=Count('article')
        ).values_list('name', 'count_num', 'pk')
        # 查询各标签下的文章及文章数
        tag_obj = models.Tag.objects.filter(blog=blog).annotate(
            count_num=Count('article')
        ).values_list('name', 'count_num', 'pk')
        # 查询各日期下的文章及文章数
        sort_by_month_obj = models.Article.objects.filter(blog=blog).annotate(
            month=functions.TruncMonth('create_time')).values_list('month').annotate(
            num=Count('id')).values_list('month', 'num')
        return locals()
