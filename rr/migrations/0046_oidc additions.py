# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-06-07 10:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rr', '0045_auto_20190607_1327'),
    ]

    operations = [
        migrations.CreateModel(
            name='GrantType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='Grant type')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='RedirectUri',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uri', models.CharField(max_length=255, verbose_name='Redirect URI')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('end_at', models.DateTimeField(blank=True, null=True, verbose_name='Entry end time')),
                ('validated', models.DateTimeField(blank=True, null=True, verbose_name='Validated on')),
            ],
        ),
        migrations.CreateModel(
            name='ResponseType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, verbose_name='Response type')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='attribute',
            name='oidc_scope',
            field=models.CharField(blank=True, max_length=255, verbose_name='Attribute scope for OIDC'),
        ),
        migrations.AddField(
            model_name='attribute',
            name='public_oidc',
            field=models.BooleanField(default=True, verbose_name='Show in OIDC attribute list'),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='application_type',
            field=models.CharField(choices=[('web', 'web'), ('native', 'native')], default='web', max_length=8, verbose_name='Application type'),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='encrypted_client_secret',
            field=models.TextField(blank=True, verbose_name='Client secret'),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='subject_identifier',
            field=models.CharField(blank=True, choices=[('public', 'public'), ('pairwise', 'pairwise')], max_length=8, verbose_name='Subject identifier'),
        ),
        migrations.AlterField(
            model_name='serviceprovider',
            name='service_type',
            field=models.CharField(choices=[('saml', 'SAML / Shibboleth'), ('ldap', 'LDAP'), ('oidc', 'OIDC')], max_length=10, verbose_name='Service type (SAML/LDAP)'),
        ),
        migrations.AddField(
            model_name='redirecturi',
            name='sp',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rr.ServiceProvider'),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='grant_types',
            field=models.ManyToManyField(blank=True, to='rr.GrantType'),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='response_types',
            field=models.ManyToManyField(blank=True, to='rr.ResponseType'),
        ),
    ]