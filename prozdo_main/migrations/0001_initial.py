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
            name='Comment',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('body', models.TextField(blank=True, verbose_name='Содержимое')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('history_type', models.IntegerField(choices=[(1, 'Комментарий создан'), (2, 'Комментарий сохранен'), (3, 'Комментарий оценен'), (4, 'Пост создан'), (5, 'Пост сохранен'), (6, 'Пост оценен'), (7, 'Жалоба на коммент'), (8, 'Жалоба на пост')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user_points', models.PositiveIntegerField(default=0, blank=True)),
                ('author_points', models.PositiveIntegerField(default=0, blank=True)),
                ('author', models.ForeignKey(related_name='history_author', null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('title', models.CharField(verbose_name='Название', max_length=500)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('alias', models.CharField(blank=True, max_length=800)),
                ('post_type', models.IntegerField(choices=[(1, 'Препарат'), (2, 'Блог'), (3, 'Форум'), (5, 'Компонент'), (4, 'Косметика'), (6, 'Бренд'), (7, 'Форма выпуска препарата'), (8, 'Форма выпуска косметики'), (9, 'Линия косметики'), (10, 'Область применения косметики'), (11, 'Област применения препарата'), (12, 'Категория')], verbose_name='Вид записи')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('post_ptr', models.OneToOneField(serialize=False, to='prozdo_main.Post', primary_key=True, auto_created=True, parent_link=True)),
                ('body', models.TextField(blank=True, verbose_name='Содержимое')),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('post_ptr', models.OneToOneField(serialize=False, to='prozdo_main.Post', primary_key=True, auto_created=True, parent_link=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('post_ptr', models.OneToOneField(serialize=False, to='prozdo_main.Post', primary_key=True, auto_created=True, parent_link=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('post_ptr', models.OneToOneField(serialize=False, to='prozdo_main.Post', primary_key=True, auto_created=True, parent_link=True)),
                ('body', models.TextField(blank=True, verbose_name='Содержимое')),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Cosmetics',
            fields=[
                ('post_ptr', models.OneToOneField(serialize=False, to='prozdo_main.Post', primary_key=True, auto_created=True, parent_link=True)),
                ('body', models.TextField(blank=True, verbose_name='Содержимое')),
                ('brand', models.ForeignKey(verbose_name='Бренд', to='prozdo_main.Brand')),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='CosmeticsDosageForm',
            fields=[
                ('post_ptr', models.OneToOneField(serialize=False, to='prozdo_main.Post', primary_key=True, auto_created=True, parent_link=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='CosmeticsLine',
            fields=[
                ('post_ptr', models.OneToOneField(serialize=False, to='prozdo_main.Post', primary_key=True, auto_created=True, parent_link=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='CosmeticsUsageArea',
            fields=[
                ('post_ptr', models.OneToOneField(serialize=False, to='prozdo_main.Post', primary_key=True, auto_created=True, parent_link=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Drug',
            fields=[
                ('post_ptr', models.OneToOneField(serialize=False, to='prozdo_main.Post', primary_key=True, auto_created=True, parent_link=True)),
                ('body', models.TextField(blank=True, verbose_name='Содержимое')),
                ('features', models.TextField(blank=True, verbose_name='Особенности')),
                ('indications', models.TextField(blank=True, verbose_name='Показания')),
                ('priem', models.TextField(blank=True, verbose_name='Схема приема')),
                ('dosage_form', models.TextField(blank=True, verbose_name='Формы выпуска')),
                ('contra_indications', models.TextField(blank=True, verbose_name='Противопоказания')),
                ('side_effects', models.TextField(blank=True, verbose_name='Побочные эффекты')),
                ('compound', models.TextField(blank=True, verbose_name='Состав')),
                ('components', models.ManyToManyField(verbose_name='Состав', to='prozdo_main.Component')),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='DrugDosageForm',
            fields=[
                ('post_ptr', models.OneToOneField(serialize=False, to='prozdo_main.Post', primary_key=True, auto_created=True, parent_link=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='DrugUsageArea',
            fields=[
                ('post_ptr', models.OneToOneField(serialize=False, to='prozdo_main.Post', primary_key=True, auto_created=True, parent_link=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('post_ptr', models.OneToOneField(serialize=False, to='prozdo_main.Post', primary_key=True, auto_created=True, parent_link=True)),
                ('body', models.TextField(blank=True, verbose_name='Содержимое')),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.AddField(
            model_name='history',
            name='post',
            field=models.ForeignKey(to='prozdo_main.Post', related_name='history_post'),
        ),
        migrations.AddField(
            model_name='history',
            name='user',
            field=models.ForeignKey(related_name='history_user', null=True, blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(to='prozdo_main.Post'),
        ),
        migrations.AddField(
            model_name='history',
            name='comment',
            field=models.ForeignKey(related_name='history_comment', null=True, blank=True, to='prozdo_main.Component'),
        ),
        migrations.AddField(
            model_name='drug',
            name='dosage_forms',
            field=models.ManyToManyField(verbose_name='Формы выпуска', to='prozdo_main.DrugDosageForm'),
        ),
        migrations.AddField(
            model_name='drug',
            name='usage_areas',
            field=models.ManyToManyField(verbose_name='Область применения', to='prozdo_main.DrugUsageArea'),
        ),
        migrations.AddField(
            model_name='cosmetics',
            name='dosage_forms',
            field=models.ManyToManyField(verbose_name='Формы выпуска', to='prozdo_main.CosmeticsDosageForm'),
        ),
        migrations.AddField(
            model_name='cosmetics',
            name='line',
            field=models.ForeignKey(verbose_name='Линия', to='prozdo_main.CosmeticsLine'),
        ),
        migrations.AddField(
            model_name='cosmetics',
            name='usage_areas',
            field=models.ManyToManyField(verbose_name='Область применения', to='prozdo_main.CosmeticsUsageArea'),
        ),
    ]
