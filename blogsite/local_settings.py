import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 基础配置
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_TZ = False  # 影响数据库自动生成的时间字段。True:用UTC时间格式；False:根据TIME_ZONE设置时间格式
# DEBUG = False
# ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'my_blog',
        'USER': 'root',
        'PASSWORD': 'jjb000522',
        'HOST': '106.55.134.35',
        'PORT': 3306,
        'CHARSET': 'utf8',
    }
}
# 登录跳转全局配置
LOGIN_URL = '/login/'

# 如果用UserInfo替代auth_user表，添加一下配置
AUTH_USER_MODEL = 'web.User'

# 用户文件上传保存路径配置
MEDIA_ROOT = os.path.join(BASE_DIR,'file')
