# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-12 10:07
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rr", "0012_auto_20180111_1050"),
    ]

    operations = [
        migrations.AddField(
            model_name="serviceprovider",
            name="history",
            field=models.IntegerField(null=True, verbose_name="History key"),
        ),
        migrations.AlterField(
            model_name="serviceprovider",
            name="name_format_persistent",
            field=models.BooleanField(default=False, verbose_name="nameid-format:persistent"),
        ),
        migrations.AlterField(
            model_name="serviceprovider",
            name="name_format_transient",
            field=models.BooleanField(default=False, verbose_name="nameid-format:transient"),
        ),
    ]
