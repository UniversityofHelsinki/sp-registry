# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-04 07:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rr', '0007_auto_20180103_1018'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribute',
            name='nameformat',
            field=models.CharField(default='1', max_length=255, verbose_name='Attribute NameFormat'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='attribute',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Attribute FriendlyName'),
        ),
    ]
