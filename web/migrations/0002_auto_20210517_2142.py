# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2021-05-17 21:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.BigIntegerField(null=True, verbose_name='手机号'),
        ),
    ]
