# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-18 14:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('researcher', '0002_load_initial_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='researcher',
            name='email',
            field=models.CharField(max_length=100, null=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='researcher',
            name='phone',
            field=models.CharField(max_length=100, null=True, verbose_name='Phone'),
        ),
    ]