# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-08-08 07:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


# Inspired by Django doc:
# https://docs.djangoproject.com/en/1.9/ref/contrib/sites/#enabling-the-sites-framework
def set_site_domain(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    Site.objects.create(
        id=settings.SITE_ID,
        domain=settings.SITE_DOMAIN_NAME,
        name=settings.SITE_DOMAIN_NAME
    )


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255)),
                ('_h1', models.CharField(blank=True, default='', max_length=255)),
                ('keywords', models.CharField(blank=True, default='', max_length=255)),
                ('description', models.TextField(blank=True, default='')),
                ('slug', models.SlugField(blank=True, max_length=255)),
                ('route', models.SlugField(blank=True, max_length=255, null=True)),
                ('_menu_title', models.CharField(blank=True, max_length=30, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('position', models.IntegerField(default=0)),
                ('type', models.CharField(blank=True, default='page', max_length=255)),
                ('content', models.TextField(blank=True, null=True)),
                ('seo_text', models.TextField(blank=True, null=True)),
                ('_date_published', models.DateField(auto_now_add=True, null=True)),
                ('_parent', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='pages.Page')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='page',
            unique_together=set([('type', 'slug')]),
        ),
        migrations.RunPython(set_site_domain),
    ]
