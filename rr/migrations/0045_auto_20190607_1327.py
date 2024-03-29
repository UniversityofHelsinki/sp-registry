# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-06-07 10:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rr", "0044_serviceprovider_uses_ldapauth"),
    ]

    operations = [
        migrations.AlterField(
            model_name="serviceprovider",
            name="uses_ldapauth",
            field=models.BooleanField(default=False, verbose_name="Does this service use the LDAPAuth proxy?"),
        ),
    ]
