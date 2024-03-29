# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-22 12:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rr", "0018_auto_20180119_1330"),
    ]

    operations = [
        migrations.AddField(
            model_name="serviceprovider",
            name="admin_notes",
            field=models.TextField(blank=True, verbose_name="Admin notes"),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="autoupdate_idp_metadata",
            field=models.BooleanField(default=False, verbose_name="Does SP automatically update IdP metadata?"),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="notes",
            field=models.TextField(blank=True, verbose_name="Additional notes"),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="saml_product",
            field=models.CharField(blank=True, max_length=255, verbose_name="SAML product this service is using"),
        ),
    ]
