# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-29 12:41
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Attribute",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Attribute name")),
                ("info", models.TextField(verbose_name="Attribute information")),
                ("oid", models.CharField(max_length=255, verbose_name="Attribute OID")),
                ("public", models.BooleanField(default=True, verbose_name="Show in attribute list")),
            ],
        ),
        migrations.CreateModel(
            name="ServiceProvider",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("entity_id", models.CharField(max_length=255, verbose_name="Entity Id")),
                ("name_fi", models.CharField(max_length=255, verbose_name="Service Name (Finnish)")),
                ("name_en", models.CharField(blank=True, max_length=255, verbose_name="Service Name (English)")),
                ("name_sv", models.CharField(blank=True, max_length=255, verbose_name="Service Name (Swedish)")),
                (
                    "description_fi",
                    models.CharField(blank=True, max_length=255, verbose_name="Service Description (Finnish)"),
                ),
                (
                    "description_en",
                    models.CharField(blank=True, max_length=255, verbose_name="Service Description (English)"),
                ),
                (
                    "description_sv",
                    models.CharField(blank=True, max_length=255, verbose_name="Service Description (Swedish)"),
                ),
                (
                    "privacypolicy_fi",
                    models.URLField(blank=True, max_length=255, verbose_name="Privacy Policy URL (Finnish)"),
                ),
                (
                    "privacypolicy_en",
                    models.URLField(blank=True, max_length=255, verbose_name="Privacy Policy URL (English)"),
                ),
                (
                    "privacypolicy_sv",
                    models.URLField(blank=True, max_length=255, verbose_name="Privacy Policy URL (Swedish)"),
                ),
                ("login_page_url", models.URLField(blank=True, max_length=255, verbose_name="Service Login Page URL")),
                (
                    "discovery_service_url",
                    models.URLField(blank=True, max_length=255, verbose_name="Discovery Service URL"),
                ),
                (
                    "name_format_transient",
                    models.BooleanField(
                        default=False, verbose_name="urn:oasis:names:tc:SAML:2.0:nameid-format:transient"
                    ),
                ),
                (
                    "name_format_persistent",
                    models.BooleanField(
                        default=False, verbose_name="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent"
                    ),
                ),
                (
                    "encyrpt_attribute_assertions",
                    models.BooleanField(default=False, verbose_name="Encrypt attribute assertions"),
                ),
                ("production", models.BooleanField(default=False, verbose_name="Publish to production servers")),
                ("test", models.BooleanField(default=False, verbose_name="Publish to test servers")),
                ("updated", models.DateTimeField(blank=True, null=True, verbose_name="Updated at")),
                ("end_at", models.DateTimeField(blank=True, null=True, verbose_name="Entry end time")),
                ("validated", models.BooleanField(default=False, verbose_name="Validated")),
                ("admins", models.ManyToManyField(related_name="admins", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="SPAttribute",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reason", models.CharField(max_length=255, verbose_name="Reason for the attribute requisition")),
                ("updated", models.DateTimeField(blank=True, null=True, verbose_name="Updated at")),
                ("validated", models.DateTimeField(blank=True, null=True, verbose_name="Validated on")),
                ("attribute", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="rr.Attribute")),
                ("sp", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="rr.ServiceProvider")),
            ],
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="attributes",
            field=models.ManyToManyField(through="rr.SPAttribute", to="rr.Attribute"),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Updated by",
            ),
        ),
    ]
