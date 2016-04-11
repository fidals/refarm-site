# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_page_page_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='alias',
        ),
        migrations.RemoveField(
            model_name='post',
            name='is_text_published',
        ),
        migrations.AlterField(
            model_name='post',
            name='type',
            field=models.CharField(choices=[('navigation', 'Навигация'), ('news', 'Новости'), ('article', 'Статьи')], max_length=100, default='navigation'),
        ),
    ]
