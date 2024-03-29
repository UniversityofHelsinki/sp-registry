# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-02 09:54
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rr", "0004_auto_20180102_0812"),
    ]

    operations = [
        migrations.CreateModel(
            name="Contact",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("administrative", "Administrative"),
                            ("technical", "Technical"),
                            ("support", "Support"),
                        ],
                        max_length=30,
                        verbose_name="Contact Type",
                    ),
                ),
                ("firstname", models.CharField(blank=True, max_length=50, verbose_name="First Name")),
                ("lastname", models.CharField(blank=True, max_length=50, verbose_name="Last Name")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="E-Mail")),
                ("created", models.DateTimeField(blank=True, null=True, verbose_name="Created at")),
                ("end_at", models.DateTimeField(blank=True, null=True, verbose_name="Entry end time")),
                ("sp", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="rr.ServiceProvider")),
            ],
        ),
    ]
