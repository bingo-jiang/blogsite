import django
import os
import sys

# 创建与Django相匹配的环境
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'blogsite.settings')
django.setup()
# 正式操作
from web import models  # 操作所用库，不能放到上面的环境库中
from bs4 import BeautifulSoup
# Create your tests here.
obj=models.Article.objects.filter(id=7).first()
content=obj.content
soup = BeautifulSoup(content, 'html.parser')
res=str(soup.text[0:128])
models.Article.objects.filter(id=7).update(desc=res)
print(res)