# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-25 10:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rr', '0021_auto_20180125_1007'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serviceprovider',
            name='discovery_service_url',
        ),
        migrations.AddField(
            model_name='attribute',
            name='schemalink',
            field=models.BooleanField(default=True, verbose_name='Show link to funetEduPerson-schema'),
        ),
        migrations.AlterField(
            model_name='serviceprovider',
            name='sign_assertions',
            field=models.BooleanField(default=True, verbose_name='Sign SSO assertions'),
        ),
        migrations.AlterField(
            model_name='serviceprovider',
            name='sign_requests',
            field=models.BooleanField(default=False, verbose_name='Sign SSO requests'),
        ),
        migrations.AlterField(
            model_name='serviceprovider',
            name='sign_responses',
            field=models.BooleanField(default=False, verbose_name='Sign SSO responses'),
        ),
    ]