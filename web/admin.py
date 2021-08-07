from django.contrib import admin
from web import models
# Register your models here.
admin.site.register(models.User)
admin.site.register(models.BlogSite)
admin.site.register(models.Category)
admin.site.register(models.Tag)
admin.site.register(models.Comment)
admin.site.register(models.Article)
admin.site.register(models.UpAndDown)
admin.site.register(models.ArticleToTag)