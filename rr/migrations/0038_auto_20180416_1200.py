# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-16 09:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rr', '0037_usergroup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceprovider',
            name='entity_id',
            field=models.CharField(max_length=255, verbose_name='Entity Id'),
        ),
    ]