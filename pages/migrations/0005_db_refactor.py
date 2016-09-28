# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-10-10 14:23
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_auto_20160909_1100'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='date_published',
            field=models.DateField(blank=True, default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='page',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='pages.Page'),
        ),
        migrations.AddField(
            model_name='page',
            name='related_model_name',
            field=models.CharField(blank=True, editable=False, max_length=255),
        ),
        migrations.AlterField(
            model_name='page',
            name='_menu_title',
            field=models.CharField(blank=True, help_text='This field will be shown in the breadcrumbs, menu items and etc.', max_length=180),
        ),
        migrations.AlterField(
            model_name='page',
            name='_title',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='page',
            name='content',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='h1',
            field=models.CharField(max_length=255, blank=False),
        ),
        migrations.AlterField(
            model_name='page',
            name='position',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='page',
            name='seo_text',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='slug',
            field=models.SlugField(blank=True, max_length=400),
        ),
        migrations.AlterField(
            model_name='page',
            name='type',
            field=models.CharField(default='flat', editable=False, max_length=100),
        ),
        migrations.AlterField(
            model_name='page',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='keywords',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterUniqueTogether(
            name='page',
            unique_together=set([('type', 'slug', 'related_model_name')]),
        ),
        migrations.RemoveField(
            model_name='page',
            name='_date_published',
        ),
        migrations.CreateModel(
            name='CustomPage',
            fields=[
            ],
            options={
                'proxy': True,
                'abstract': False,
            },
            bases=('pages.page',),
        ),
        migrations.CreateModel(
            name='FlatPage',
            fields=[
            ],
            options={
                'proxy': True,
                'abstract': False,
            },
            bases=('pages.page',),
        ),
        migrations.CreateModel(
            name='ModelPage',
            fields=[
            ],
            options={
                'proxy': True,
                'abstract': False,
            },
            bases=('pages.page',),
        ),
    ]
