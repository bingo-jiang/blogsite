# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2021-05-18 21:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_auto_20210518_2114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.FileField(default='avatar/default.jpg', upload_to='avatar/'),
        ),
    ]
