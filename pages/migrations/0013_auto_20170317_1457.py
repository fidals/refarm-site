# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-17 14:57
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0012_auto_20170301_0020'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='custompage',
            options={'verbose_name': 'Custom Page', 'verbose_name_plural': 'Custom Pages'},
        ),
        migrations.AlterModelOptions(
            name='flatpage',
            options={'verbose_name': 'Flat Page', 'verbose_name_plural': 'Flat Pages'},
        ),
        migrations.AlterModelOptions(
            name='page',
            options={'verbose_name': 'Page', 'verbose_name_plural': 'Pages'},
        ),
        migrations.AlterField(
            model_name='page',
            name='content',
            field=models.TextField(blank=True, verbose_name='content'),
        ),
        migrations.AlterField(
            model_name='page',
            name='date_published',
            field=models.DateField(blank=True, db_index=True, default=datetime.date.today, verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='page',
            name='description',
            field=models.TextField(blank=True, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='page',
            name='is_active',
            field=models.BooleanField(db_index=True, default=True, verbose_name='is active'),
        ),
        migrations.AlterField(
            model_name='page',
            name='keywords',
            field=models.CharField(blank=True, max_length=255, verbose_name='keywords'),
        ),
        migrations.AlterField(
            model_name='page',
            name='menu_title',
            field=models.CharField(blank=True, help_text='This field will be shown in the breadcrumbs, menu items and etc.', max_length=255, verbose_name='menu title'),
        ),
        migrations.AlterField(
            model_name='page',
            name='name',
            field=models.CharField(db_index=True, default='', max_length=255, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='page',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='pages.Page', verbose_name='parent'),
        ),
        migrations.AlterField(
            model_name='page',
            name='position',
            field=models.IntegerField(blank=True, db_index=True, default=0, verbose_name='position'),
        ),
        migrations.AlterField(
            model_name='page',
            name='seo_text',
            field=models.TextField(blank=True, verbose_name='seo text'),
        ),
        migrations.AlterField(
            model_name='page',
            name='slug',
            field=models.SlugField(blank=True, max_length=400, verbose_name='slug'),
        ),
        migrations.AlterField(
            model_name='page',
            name='title',
            field=models.TextField(blank=True, verbose_name='title'),
        ),
    ]
