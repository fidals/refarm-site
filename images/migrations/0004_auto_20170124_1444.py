# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-01-24 14:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0003_auto_20161027_0940'),
    ]

    operations = [
        migrations.RenameField(
            model_name='image',
            old_name='_title',
            new_name='title',
        ),
    ]