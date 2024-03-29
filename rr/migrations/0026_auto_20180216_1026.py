# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-02-16 10:26
from __future__ import unicode_literals

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rr", "0025_auto_20180212_0946"),
    ]

    operations = [
        migrations.CreateModel(
            name="Organization",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name_fi", models.CharField(blank=True, max_length=255, verbose_name="Organization Name (Finnish)")),
                ("name_en", models.CharField(blank=True, max_length=255, verbose_name="Organization Name (English)")),
                ("name_sv", models.CharField(blank=True, max_length=255, verbose_name="Organization Name (Swedish)")),
                (
                    "description_fi",
                    models.CharField(blank=True, max_length=255, verbose_name="Organization Description (Finnish)"),
                ),
                (
                    "description_en",
                    models.CharField(blank=True, max_length=255, verbose_name="Organization Description (English)"),
                ),
                (
                    "description_sv",
                    models.CharField(blank=True, max_length=255, verbose_name="Organization Description (Swedish)"),
                ),
                ("url_fi", models.URLField(blank=True, max_length=255, verbose_name="Organization URL (Finnish)")),
                ("url_en", models.URLField(blank=True, max_length=255, verbose_name="Organization URL (English)")),
                ("url_sv", models.URLField(blank=True, max_length=255, verbose_name="Organization URL (Swedish)")),
            ],
        ),
        migrations.AlterField(
            model_name="serviceprovider",
            name="admins",
            field=models.ManyToManyField(blank=True, related_name="admins", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="serviceprovider",
            name="description_en",
            field=models.CharField(
                blank=True,
                max_length=140,
                validators=[django.core.validators.MaxLengthValidator(140)],
                verbose_name="Service Description (English)",
            ),
        ),
        migrations.AlterField(
            model_name="serviceprovider",
            name="description_fi",
            field=models.CharField(
                blank=True,
                max_length=140,
                validators=[django.core.validators.MaxLengthValidator(140)],
                verbose_name="Service Description (Finnish)",
            ),
        ),
        migrations.AlterField(
            model_name="serviceprovider",
            name="description_sv",
            field=models.CharField(
                blank=True,
                max_length=140,
                validators=[django.core.validators.MaxLengthValidator(140)],
                verbose_name="Service Description (Swedish)",
            ),
        ),
        migrations.AlterField(
            model_name="serviceprovider",
            name="name_en",
            field=models.CharField(
                blank=True,
                max_length=70,
                validators=[django.core.validators.MaxLengthValidator(70)],
                verbose_name="Service Name (English)",
            ),
        ),
        migrations.AlterField(
            model_name="serviceprovider",
            name="name_fi",
            field=models.CharField(
                blank=True,
                max_length=70,
                validators=[django.core.validators.MaxLengthValidator(70)],
                verbose_name="Service Name (Finnish)",
            ),
        ),
        migrations.AlterField(
            model_name="serviceprovider",
            name="name_sv",
            field=models.CharField(
                blank=True,
                max_length=70,
                validators=[django.core.validators.MaxLengthValidator(70)],
                verbose_name="Service Name (Swedish)",
            ),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="rr.Organization",
                verbose_name="Organization",
            ),
        ),
    ]
