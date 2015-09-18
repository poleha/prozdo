# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sorl.thumbnail.fields
from django.conf import settings
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created', models.DateTimeField(blank=True)),
                ('updated', models.DateField(null=True, blank=True)),
                ('username', models.CharField(max_length=256, verbose_name='Имя')),
                ('email', models.EmailField(max_length=254, verbose_name='E-Mail')),
                ('post_mark', models.IntegerField(null=True, verbose_name='Оценка', blank=True, choices=[(1, '1'), (1, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('body', models.TextField(verbose_name='Сообщение')),
                ('ip', models.CharField(max_length=15)),
                ('session_key', models.TextField(blank=True)),
                ('consult_required', models.BooleanField(default=False, verbose_name='Нужна консультация провизора')),
                ('status', models.IntegerField(choices=[(1, 'На согласовании'), (2, 'Опубликован')], verbose_name='Статус')),
                ('key', models.CharField(max_length=128, blank=True)),
                ('confirmed', models.BooleanField(default=False)),
                ('old_id', models.PositiveIntegerField(null=True, blank=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(null=True, blank=True, related_name='children', to='prozdo_main.Comment')),
            ],
            options={
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created', models.DateTimeField(blank=True)),
                ('updated', models.DateField(null=True, blank=True)),
                ('history_type', models.IntegerField(choices=[(1, 'Комментарий создан'), (2, 'Комментарий сохранен'), (3, 'Комментарий оценен'), (4, 'Пост создан'), (5, 'Пост сохранен'), (6, 'Пост оценен'), (7, 'Жалоба на коммент'), (8, 'Жалоба на пост')])),
                ('user_points', models.PositiveIntegerField(default=0, blank=True)),
                ('ip', models.CharField(null=True, max_length=15, blank=True)),
                ('session_key', models.TextField(blank=True)),
                ('mark', models.IntegerField(null=True, verbose_name='Оценка', blank=True, choices=[(1, '1'), (1, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('old_id', models.PositiveIntegerField(null=True, blank=True)),
                ('author', models.ForeignKey(null=True, blank=True, related_name='history_author', to=settings.AUTH_USER_MODEL)),
                ('comment', models.ForeignKey(null=True, blank=True, related_name='history_comment', to='prozdo_main.Comment')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Mail',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created', models.DateTimeField(blank=True)),
                ('updated', models.DateField(null=True, blank=True)),
                ('mail_type', models.PositiveIntegerField(choices=[(1, 'Подтверждение отзыва'), (2, 'Регистрация пользователя'), (1, 'Сброс пароля')])),
                ('subject', models.TextField()),
                ('body_html', models.TextField(default='', blank=True)),
                ('body_text', models.TextField(default='', blank=True)),
                ('email', models.EmailField(max_length=254)),
                ('ip', models.CharField(null=True, max_length=15, blank=True)),
                ('session_key', models.TextField(null=True, blank=True)),
                ('user', models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created', models.DateTimeField(blank=True)),
                ('updated', models.DateField(null=True, blank=True)),
                ('title', models.CharField(max_length=500, verbose_name='Название')),
                ('alias', models.CharField(verbose_name='Синоним', blank=True, max_length=800)),
                ('post_type', models.IntegerField(choices=[(1, 'Препарат'), (2, 'Блог'), (3, 'Форум'), (5, 'Компонент'), (4, 'Косметика'), (6, 'Бренд'), (7, 'Форма выпуска препарата'), (8, 'Форма выпуска косметики'), (9, 'Линия косметики'), (10, 'Область применения косметики'), (11, 'Област применения препарата'), (12, 'Категория')], verbose_name='Вид записи')),
                ('status', models.IntegerField(default=1, choices=[(1, 'Проект'), (2, 'Опубликован')], verbose_name='Статус')),
                ('old_id', models.PositiveIntegerField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created', models.DateTimeField(blank=True)),
                ('updated', models.DateField(null=True, blank=True)),
                ('role', models.PositiveIntegerField(default=1, choices=[(1, 'Обычный пользователь'), (2, 'Автор'), (3, 'Врач'), (33, 'Админ')], blank=True)),
                ('image', sorl.thumbnail.fields.ImageField(upload_to='user_profile', null=True, verbose_name='Изображение', blank=True)),
                ('receive_messages', models.BooleanField(default=True, verbose_name='Получать e-mail сообщения с сайта')),
                ('first_name', models.CharField(verbose_name='Имя', blank=True, max_length=800)),
                ('last_name', models.CharField(verbose_name='Фамилия', blank=True, max_length=800)),
                ('old_id', models.PositiveIntegerField(null=True, blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='user_profile')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, serialize=False, primary_key=True, to='prozdo_main.Post')),
                ('short_body', models.TextField(verbose_name='Анонс', blank=True)),
                ('body', models.TextField(verbose_name='Содержимое', blank=True)),
                ('image', sorl.thumbnail.fields.ImageField(upload_to='blog', null=True, verbose_name='Изображение', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, serialize=False, primary_key=True, to='prozdo_main.Post')),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, serialize=False, primary_key=True, to='prozdo_main.Post')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(null=True, blank=True, related_name='children', to='prozdo_main.Category')),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post', models.Model),
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, serialize=False, primary_key=True, to='prozdo_main.Post')),
                ('body', models.TextField(verbose_name='Содержимое', blank=True)),
                ('component_type', models.IntegerField(choices=[(1, 'Витамин'), (2, 'Минеральное вещество'), (3, 'Растение'), (4, 'Прочее')], verbose_name='Тип компонента')),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Cosmetics',
            fields=[
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, serialize=False, primary_key=True, to='prozdo_main.Post')),
                ('body', models.TextField(verbose_name='Содержимое', blank=True)),
                ('image', sorl.thumbnail.fields.ImageField(upload_to='cosmetics', null=True, verbose_name='Изображение', blank=True)),
                ('brand', models.ForeignKey(to='prozdo_main.Brand', verbose_name='Бренд')),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='CosmeticsDosageForm',
            fields=[
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, serialize=False, primary_key=True, to='prozdo_main.Post')),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='CosmeticsLine',
            fields=[
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, serialize=False, primary_key=True, to='prozdo_main.Post')),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='CosmeticsUsageArea',
            fields=[
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, serialize=False, primary_key=True, to='prozdo_main.Post')),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Drug',
            fields=[
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, serialize=False, primary_key=True, to='prozdo_main.Post')),
                ('body', models.TextField(verbose_name='Содержимое', blank=True)),
                ('features', models.TextField(verbose_name='Особенности', blank=True)),
                ('indications', models.TextField(verbose_name='Показания', blank=True)),
                ('application_scheme', models.TextField(verbose_name='Схема приема', blank=True)),
                ('dosage_form', models.TextField(verbose_name='Формы выпуска', blank=True)),
                ('contra_indications', models.TextField(verbose_name='Противопоказания', blank=True)),
                ('side_effects', models.TextField(verbose_name='Побочные эффекты', blank=True)),
                ('compound', models.TextField(verbose_name='Состав', blank=True)),
                ('image', sorl.thumbnail.fields.ImageField(upload_to='drug', null=True, verbose_name='Изображение', blank=True)),
                ('category', mptt.fields.TreeManyToManyField(verbose_name='Категория', blank=True, to='prozdo_main.Category')),
                ('components', models.ManyToManyField(verbose_name='Состав', blank=True, to='prozdo_main.Component')),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='DrugDosageForm',
            fields=[
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, serialize=False, primary_key=True, to='prozdo_main.Post')),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='DrugUsageArea',
            fields=[
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, serialize=False, primary_key=True, to='prozdo_main.Post')),
            ],
            options={
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.AddField(
            model_name='history',
            name='post',
            field=models.ForeignKey(related_name='history_post', to='prozdo_main.Post'),
        ),
        migrations.AddField(
            model_name='history',
            name='user',
            field=models.ForeignKey(null=True, blank=True, related_name='history_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(related_name='comments', to='prozdo_main.Post'),
        ),
        migrations.AddField(
            model_name='comment',
            name='updater',
            field=models.ForeignKey(null=True, blank=True, related_name='updated_comments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(null=True, blank=True, related_name='comments', to=settings.AUTH_USER_MODEL),
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
            field=models.ManyToManyField(to='prozdo_main.CosmeticsDosageForm', verbose_name='Формы выпуска'),
        ),
        migrations.AddField(
            model_name='cosmetics',
            name='line',
            field=models.ForeignKey(null=True, to='prozdo_main.CosmeticsLine', blank=True, verbose_name='Линейка'),
        ),
        migrations.AddField(
            model_name='cosmetics',
            name='usage_areas',
            field=models.ManyToManyField(to='prozdo_main.CosmeticsUsageArea', verbose_name='Область применения'),
        ),
        migrations.AddField(
            model_name='blog',
            name='category',
            field=mptt.fields.TreeManyToManyField(to='prozdo_main.Category', verbose_name='Категория'),
        ),
    ]
