# Generated by Django 4.2.2 on 2023-07-13 13:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rr", "0055_add_privacy_policy"),
    ]

    operations = [
        migrations.AlterField(
            model_name="spattribute",
            name="attribute",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="spattributes", to="rr.attribute"
            ),
        ),
        migrations.AlterField(
            model_name="spattribute",
            name="sp",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="spattributes", to="rr.serviceprovider"
            ),
        ),
    ]
