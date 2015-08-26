# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Alias',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('post_cls', models.CharField(max_length=100)),
                ('post_id', models.PositiveIntegerField()),
                ('alias', models.CharField(unique=True, max_length=800, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=500, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('body', models.TextField(verbose_name='Содержимое', blank=True)),
                ('alias', models.OneToOneField(to='prozdo_main.Alias', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=500, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('alias', models.OneToOneField(to='prozdo_main.Alias', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=500, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('post_cls', models.CharField(max_length=100)),
                ('post_id', models.PositiveIntegerField()),
                ('body', models.TextField(verbose_name='Содержимое', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=500, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('body', models.TextField(verbose_name='Содержимое', blank=True)),
                ('alias', models.OneToOneField(to='prozdo_main.Alias', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Cosmetics',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=500, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('body', models.TextField(verbose_name='Содержимое', blank=True)),
                ('alias', models.OneToOneField(to='prozdo_main.Alias', null=True, blank=True)),
                ('brand', models.ForeignKey(to='prozdo_main.Brand', verbose_name='Бренд')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CosmeticsLine',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=500, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CosmeticsUsageArea',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=500, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CosteticsDosageForm',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=500, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Drug',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=500, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('body', models.TextField(verbose_name='Содержимое', blank=True)),
                ('features', models.TextField(verbose_name='Особенности', blank=True)),
                ('indications', models.TextField(verbose_name='Показания', blank=True)),
                ('priem', models.TextField(verbose_name='Схема приема', blank=True)),
                ('dosage_form', models.TextField(verbose_name='Формы выпуска', blank=True)),
                ('contra_indications', models.TextField(verbose_name='Противопоказания', blank=True)),
                ('side_effects', models.TextField(verbose_name='Побочные эффекты', blank=True)),
                ('compound', models.TextField(verbose_name='Состав', blank=True)),
                ('alias', models.OneToOneField(to='prozdo_main.Alias', null=True, blank=True)),
                ('components', models.ManyToManyField(to='prozdo_main.Component', verbose_name='Состав')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DrugDosageForm',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=500, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DrugUsageArea',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=500, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=500, verbose_name='Название')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('body', models.TextField(verbose_name='Содержимое', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('post_cls', models.CharField(max_length=100)),
                ('post_id', models.PositiveIntegerField()),
                ('history_type', models.IntegerField(choices=[(1, 'Комментарий создан'), (2, 'Комментарий сохранен'), (3, 'Комментарий оценен'), (4, 'Пост создан'), (5, 'Пост сохранен'), (6, 'Пост оценен'), (7, 'Жалоба на коммент'), (8, 'Жалоба на пост')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user_points', models.PositiveIntegerField(default=0, blank=True)),
                ('author_points', models.PositiveIntegerField(default=0, blank=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='history_author', blank=True, null=True)),
                ('comment', models.ForeignKey(to='prozdo_main.Component', blank=True, null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='history_user', blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='drug',
            name='dosage_forms',
            field=models.ManyToManyField(to='prozdo_main.DrugDosageForm', verbose_name='Формы выпуска'),
        ),
        migrations.AddField(
            model_name='drug',
            name='usage_areas',
            field=models.ManyToManyField(to='prozdo_main.DrugUsageArea', verbose_name='Область применения'),
        ),
        migrations.AddField(
            model_name='cosmetics',
            name='dosage_forms',
            field=models.ManyToManyField(to='prozdo_main.CosteticsDosageForm', verbose_name='Формы выпуска'),
        ),
        migrations.AddField(
            model_name='cosmetics',
            name='line',
            field=models.ForeignKey(to='prozdo_main.CosmeticsLine', verbose_name='Линия'),
        ),
        migrations.AddField(
            model_name='cosmetics',
            name='usage_areas',
            field=models.ManyToManyField(to='prozdo_main.CosmeticsUsageArea', verbose_name='Область применения'),
        ),
    ]
