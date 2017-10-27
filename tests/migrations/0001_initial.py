# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-10-27 10:40
from __future__ import unicode_literals

import catalog.models
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pages', '0015_add_validation_to_template'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnotherRelatedEntity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='EcommerceTestCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, verbose_name='name')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('page', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tests_ecommercetestcategory', to='pages.Page')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='tests.EcommerceTestCategory', verbose_name='parent')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'abstract': False,
            },
            bases=(models.Model, catalog.models.AdminTreeDisplayMixin),
        ),
        migrations.CreateModel(
            name='EcommerceTestProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, verbose_name='name')),
                ('price', models.FloatField(blank=True, db_index=True, default=0, verbose_name='price')),
                ('in_stock', models.PositiveIntegerField(db_index=True, default=0, verbose_name='in stock')),
                ('is_popular', models.BooleanField(db_index=True, default=False, verbose_name='is popular')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='tests.EcommerceTestCategory')),
                ('page', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tests_ecommercetestproduct', to='pages.Page')),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'ordering': ['name'],
                'abstract': False,
            },
            bases=(models.Model, catalog.models.AdminTreeDisplayMixin),
        ),
        migrations.CreateModel(
            name='RelatedEntity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='TestCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, verbose_name='name')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('page', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tests_testcategory', to='pages.Page')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='tests.TestCategory', verbose_name='parent')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'abstract': False,
            },
            bases=(models.Model, catalog.models.AdminTreeDisplayMixin),
        ),
        migrations.CreateModel(
            name='TestCategoryWithDefaultPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, verbose_name='name')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('page', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tests_testcategorywithdefaultpage', to='pages.Page')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='tests.TestCategoryWithDefaultPage', verbose_name='parent')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'abstract': False,
            },
            bases=(models.Model, catalog.models.AdminTreeDisplayMixin),
        ),
        migrations.CreateModel(
            name='TestEntity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('slug', models.SlugField(default='/so-mock-wow/')),
                ('page', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tests_testentity', to='pages.Page')),
                ('parent', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tests.TestEntity')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TestEntityWithRelations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('another_related_entity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tests.AnotherRelatedEntity')),
                ('related_entity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tests.RelatedEntity')),
            ],
        ),
        migrations.CreateModel(
            name='TestEntityWithSync',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('page', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tests_testentitywithsync', to='pages.Page')),
                ('parent', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tests.TestEntityWithSync')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TestProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, verbose_name='name')),
                ('price', models.FloatField(blank=True, db_index=True, default=0, verbose_name='price')),
                ('in_stock', models.PositiveIntegerField(db_index=True, default=0, verbose_name='in stock')),
                ('is_popular', models.BooleanField(db_index=True, default=False, verbose_name='is popular')),
                ('category', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='tests.TestCategory')),
                ('page', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tests_testproduct', to='pages.Page')),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'ordering': ['name'],
                'abstract': False,
            },
            bases=(models.Model, catalog.models.AdminTreeDisplayMixin),
        ),
        migrations.AlterUniqueTogether(
            name='testcategorywithdefaultpage',
            unique_together={('name', 'parent')},
        ),
        migrations.AlterUniqueTogether(
            name='testcategory',
            unique_together={('name', 'parent')},
        ),
        migrations.AlterUniqueTogether(
            name='ecommercetestcategory',
            unique_together={('name', 'parent')},
        ),
    ]
