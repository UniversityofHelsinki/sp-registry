# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-01 10:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rr", "0038_auto_20180927_1148"),
    ]

    operations = [
        migrations.AddField(
            model_name="serviceprovider",
            name="can_access_all_ldap_groups",
            field=models.BooleanField(default=False, verbose_name="Service requires access to all LDAP groups"),
        ),
    ]
