# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-17 14:57
from __future__ import unicode_literals

from django.db import migrations, models
import images.models
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0004_auto_20170124_1444'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='image',
            options={'verbose_name': 'image', 'verbose_name_plural': 'images'},
        ),
        migrations.AlterField(
            model_name='image',
            name='created',
            field=models.DateField(auto_now_add=True, verbose_name='created'),
        ),
        migrations.AlterField(
            model_name='image',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='image',
            name='image',
            field=sorl.thumbnail.fields.ImageField(upload_to=images.models.model_directory_path, verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='image',
            name='is_main',
            field=models.BooleanField(db_index=True, default=False, verbose_name='is main'),
        ),
        migrations.AlterField(
            model_name='image',
            name='slug',
            field=models.SlugField(blank=True, max_length=400, verbose_name='slug'),
        ),
        migrations.AlterField(
            model_name='image',
            name='title',
            field=models.CharField(blank=True, max_length=400, verbose_name='title'),
        ),
    ]