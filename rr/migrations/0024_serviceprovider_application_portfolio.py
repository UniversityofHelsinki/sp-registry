# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-02-05 11:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rr', '0023_serviceprovider_discovery_service_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceprovider',
            name='application_portfolio',
            field=models.URLField(blank=True, max_length=255, verbose_name='Application portfolio URL'),
        ),
    ]