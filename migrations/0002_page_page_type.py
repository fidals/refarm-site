# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='type',
            field=models.CharField(max_length=100, default='article', choices=[('news', 'Новости'), ('article', 'Статьи'), ('navi', 'Навигация')]),
        ),
    ]
