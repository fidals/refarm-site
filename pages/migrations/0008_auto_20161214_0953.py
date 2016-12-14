# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-12-14 09:53
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0007_rename_private_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='date_published',
            field=models.DateField(blank=True, db_index=True, default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='page',
            name='is_active',
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='name',
            field=models.CharField(db_index=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='page',
            name='position',
            field=models.IntegerField(blank=True, db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='page',
            name='type',
            field=models.CharField(db_index=True, default='flat', editable=False, max_length=100),
        ),
    ]