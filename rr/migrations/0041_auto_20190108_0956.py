# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-01-08 07:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rr", "0040_auto_20181005_1302"),
    ]

    operations = [
        migrations.AlterField(
            model_name="testuser",
            name="firstname",
            field=models.CharField(blank=True, default="", max_length=255, verbose_name="First name"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="testuser",
            name="lastname",
            field=models.CharField(blank=True, default="", max_length=255, verbose_name="Last name"),
            preserve_default=False,
        ),
    ]
