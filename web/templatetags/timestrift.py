from django import template
from web import models
from django.db.models import Count, functions
import time, datetime

register = template.Library()


@register.simple_tag
def time_format(time_str):
    time_str = time_str.strftime('%Y-%m-%d')
    return time_str
