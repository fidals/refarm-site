# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-10-17 15:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_auto_20160909_1100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='content',
            field=models.TextField(blank=True, default=''),
        ),
    ]
