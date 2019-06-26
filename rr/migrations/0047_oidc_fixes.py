# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-06-14 09:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rr', '0046_oidc additions'),
    ]

    operations = [
        migrations.CreateModel(
            name='OIDCScope',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25, verbose_name='OIDC Scope')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.RenameField(
            model_name='attribute',
            old_name='oidc_scope',
            new_name='oidc_claim',
        ),
        migrations.AlterField(
            model_name='attribute',
            name='oidc_claim',
            field=models.CharField(blank=True, max_length=255, verbose_name='Attribute claim name for OIDC'),
        ),
        migrations.AddField(
            model_name='spattribute',
            name='oidc_id_token',
            field=models.BooleanField(default=False, verbose_name='Release in the ID Token'),
        ),
        migrations.AddField(
            model_name='spattribute',
            name='oidc_userinfo',
            field=models.BooleanField(default=False, verbose_name='Release from the userinfo endpoint'),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='oidc_scopes',
            field=models.ManyToManyField(blank=True, to='rr.OIDCScope'),
        ),
    ]