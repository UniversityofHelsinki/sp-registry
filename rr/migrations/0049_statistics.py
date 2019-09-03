# Generated by Django 2.2.3 on 2019-09-02 05:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rr', '0048_attribute_scoped'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logins', models.IntegerField(verbose_name='Number of logins')),
                ('date', models.DateField(verbose_name='Login date')),
                ('sp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rr.ServiceProvider')),
            ],
        ),
    ]
