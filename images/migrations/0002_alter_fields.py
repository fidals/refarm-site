# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-10-18 11:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='_title',
            field=models.CharField(blank=True, max_length=400),
        ),
        migrations.AlterField(
            model_name='image',
            name='created',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='image',
            name='is_main',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]