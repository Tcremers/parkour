# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-08 22:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('library', '0019_sample_is_converted'),
    ]

    operations = [
        migrations.CreateModel(
            name='LibraryPreparation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('starting_amount', models.FloatField(blank=True, null=True, verbose_name='Starting Amount')),
                ('starting_volume', models.FloatField(blank=True, null=True, verbose_name='Starting Amount')),
                ('spike_in_description', models.TextField(blank=True, null=True, verbose_name='Spike-in Description')),
                ('spike_in_volume', models.FloatField(blank=True, null=True, verbose_name='Spike-in Volume')),
                ('ul_sample', models.FloatField(blank=True, null=True, verbose_name='µl Sample')),
                ('ul_buffer', models.FloatField(blank=True, null=True, verbose_name='µl Buffer')),
                ('pcr_cycles', models.IntegerField(blank=True, null=True, verbose_name='PCR Cycles')),
                ('concentration_library', models.FloatField(blank=True, null=True, verbose_name='Concentration Library')),
                ('mean_fragment_size', models.IntegerField(blank=True, null=True, verbose_name='Mean Fragment Size')),
                ('nM', models.FloatField(blank=True, null=True, verbose_name='nM')),
            ],
            options={
                'verbose_name_plural': 'Library Preparation',
                'verbose_name': 'Library Preparation',
            },
        ),
        migrations.CreateModel(
            name='LibraryPreparationFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='benchtop_protocols/%Y/%m/%d/')),
            ],
        ),
        migrations.AddField(
            model_name='librarypreparation',
            name='file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='library_preparation.LibraryPreparationFile', verbose_name='File'),
        ),
        migrations.AddField(
            model_name='librarypreparation',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='library.Sample', verbose_name='Sample'),
        ),
    ]