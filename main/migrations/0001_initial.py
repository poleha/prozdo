# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor_uploader.fields
import ckeditor.fields
import mptt.fields
from django.conf import settings
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('created', models.DateTimeField(verbose_name='Время создания', blank=True, db_index=True)),
                ('updated', models.DateTimeField(verbose_name='Время изменения', null=True, blank=True, db_index=True)),
                ('published', models.DateTimeField(verbose_name='Время публикации', null=True, blank=True, db_index=True)),
                ('username', models.CharField(max_length=256, verbose_name='Имя')),
                ('email', models.EmailField(max_length=254, verbose_name='E-Mail')),
                ('body', models.TextField(verbose_name='Сообщение')),
                ('ip', models.CharField(max_length=300, db_index=True)),
                ('session_key', models.TextField(null=True, blank=True, db_index=True)),
                ('status', models.IntegerField(verbose_name='Статус', choices=[(1, 'На согласовании'), (2, 'Опубликован')], db_index=True)),
                ('key', models.CharField(max_length=128, blank=True)),
                ('confirmed', models.BooleanField(default=False, db_index=True)),
                ('delete_mark', models.BooleanField(verbose_name='Пометка удаления', default=False, db_index=True)),
                ('post_mark', models.IntegerField(verbose_name='Оценка', null=True, blank=True, choices=[(1, '1'), (1, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('consult_required', models.BooleanField(verbose_name='Нужна консультация провизора', default=False, db_index=True)),
                ('old_id', models.PositiveIntegerField(null=True, blank=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(null=True, to='main.Comment', blank=True, related_name='children')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('created', models.DateTimeField(verbose_name='Время создания', blank=True, db_index=True)),
                ('updated', models.DateTimeField(verbose_name='Время изменения', null=True, blank=True, db_index=True)),
                ('history_type', models.IntegerField(choices=[(1, 'Комментарий создан'), (2, 'Комментарий сохранен'), (3, 'Комментарий оценен'), (4, 'Материал создан'), (5, 'Материал сохранен'), (6, 'Материал оценен'), (7, 'Жалоба на комментарий')], db_index=True)),
                ('user_points', models.PositiveIntegerField(default=0, blank=True)),
                ('ip', models.CharField(max_length=300, null=True, blank=True, db_index=True)),
                ('session_key', models.TextField(null=True, blank=True, db_index=True)),
                ('mark', models.IntegerField(verbose_name='Оценка', null=True, blank=True, choices=[(1, '1'), (1, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('old_id', models.PositiveIntegerField(null=True, blank=True)),
                ('deleted', models.BooleanField(verbose_name='Удалена', default=False, db_index=True)),
                ('author', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True, related_name='history_author')),
                ('comment', models.ForeignKey(null=True, to='main.Comment', blank=True, related_name='history_comment')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Mail',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('created', models.DateTimeField(verbose_name='Время создания', blank=True, db_index=True)),
                ('updated', models.DateTimeField(verbose_name='Время изменения', null=True, blank=True, db_index=True)),
                ('mail_type', models.PositiveIntegerField(choices=[(1, 'Подтверждение отзыва'), (2, 'Регистрация пользователя'), (3, 'Сброс пароля'), (4, 'Ответ на отзыв'), (5, 'Подтверждение электронного адреса')], db_index=True)),
                ('subject', models.TextField()),
                ('body_html', models.TextField(default='', blank=True)),
                ('body_text', models.TextField(default='', blank=True)),
                ('email', models.EmailField(max_length=254, db_index=True)),
                ('ip', models.CharField(max_length=300, null=True, blank=True, db_index=True)),
                ('session_key', models.TextField(null=True, blank=True, db_index=True)),
                ('email_from', models.EmailField(max_length=254, db_index=True)),
                ('entity_id', models.CharField(max_length=20, blank=True, db_index=True)),
                ('user', models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('created', models.DateTimeField(verbose_name='Время создания', blank=True, db_index=True)),
                ('updated', models.DateTimeField(verbose_name='Время изменения', null=True, blank=True, db_index=True)),
                ('title', models.CharField(max_length=500, verbose_name='Название', db_index=True)),
                ('published', models.DateTimeField(verbose_name='Время публикации', null=True, blank=True, db_index=True)),
                ('alias', models.CharField(max_length=800, verbose_name='Синоним', blank=True, db_index=True)),
                ('status', models.IntegerField(verbose_name='Статус', choices=[(1, 'Проект'), (2, 'Опубликован')], default=1, db_index=True)),
                ('post_type', models.IntegerField(verbose_name='Вид записи', choices=[(1, 'Препарат'), (2, 'Блог'), (3, 'Форум'), (5, 'Компонент'), (4, 'Косметика'), (6, 'Бренд'), (7, 'Форма выпуска препарата'), (8, 'Форма выпуска косметики'), (9, 'Линия косметики'), (10, 'Область применения косметики'), (11, 'Област применения препарата'), (12, 'Категория')], db_index=True)),
                ('old_id', models.PositiveIntegerField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('created', models.DateTimeField(verbose_name='Время создания', blank=True, db_index=True)),
                ('updated', models.DateTimeField(verbose_name='Время изменения', null=True, blank=True, db_index=True)),
                ('role', models.PositiveIntegerField(choices=[(1, 'Обычный пользователь'), (2, 'Автор'), (3, 'Врач'), (33, 'Админ')], default=1, db_index=True, blank=True)),
                ('image', models.ImageField(upload_to='user_profile', verbose_name='Изображение', null=True, blank=True)),
                ('receive_messages', models.BooleanField(verbose_name='Получать e-mail сообщения с сайта', default=True, db_index=True)),
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
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, primary_key=True, to='main.Post')),
                ('short_body', models.TextField(verbose_name='Анонс', blank=True)),
                ('body', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Содержимое', blank=True)),
                ('image', sorl.thumbnail.fields.ImageField(max_length=300, verbose_name='Изображение', null=True, blank=True, upload_to='blog')),
            ],
            options={
                'ordering': ('-created',),
            },
            bases=('main.post',),
        ),
        migrations.CreateModel(
            name='BrandModel',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, primary_key=True, to='main.Post')),
            ],
            options={
                'abstract': False,
            },
            bases=('main.post',),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, primary_key=True, to='main.Post')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(null=True, to='main.Category', blank=True, related_name='children')),
            ],
            options={
                'abstract': False,
            },
            bases=('main.post', models.Model),
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, primary_key=True, to='main.Post')),
                ('body', ckeditor.fields.RichTextField(verbose_name='Содержимое', blank=True)),
                ('component_type', models.IntegerField(verbose_name='Тип компонента', choices=[(1, 'Витамин'), (2, 'Минеральное вещество'), (3, 'Растение'), (4, 'Прочее')], db_index=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('main.post',),
        ),
        migrations.CreateModel(
            name='Cosmetics',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, primary_key=True, to='main.Post')),
                ('body', ckeditor.fields.RichTextField(verbose_name='Содержимое', blank=True)),
                ('image', sorl.thumbnail.fields.ImageField(max_length=300, verbose_name='Изображение', null=True, blank=True, upload_to='cosmetics')),
                ('brand', models.ForeignKey(verbose_name='Бренд', to='main.BrandModel')),
            ],
            options={
                'abstract': False,
            },
            bases=('main.post',),
        ),
        migrations.CreateModel(
            name='CosmeticsDosageForm',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, primary_key=True, to='main.Post')),
            ],
            options={
                'abstract': False,
            },
            bases=('main.post',),
        ),
        migrations.CreateModel(
            name='CosmeticsLine',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, primary_key=True, to='main.Post')),
            ],
            options={
                'abstract': False,
            },
            bases=('main.post',),
        ),
        migrations.CreateModel(
            name='CosmeticsUsageArea',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, primary_key=True, to='main.Post')),
            ],
            options={
                'abstract': False,
            },
            bases=('main.post',),
        ),
        migrations.CreateModel(
            name='Drug',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, primary_key=True, to='main.Post')),
                ('body', ckeditor.fields.RichTextField(verbose_name='Описание', blank=True)),
                ('features', ckeditor.fields.RichTextField(verbose_name='Особенности', blank=True)),
                ('indications', ckeditor.fields.RichTextField(verbose_name='Показания', blank=True)),
                ('application_scheme', ckeditor.fields.RichTextField(verbose_name='Схема приема', blank=True)),
                ('dosage_form', ckeditor.fields.RichTextField(verbose_name='Формы выпуска', blank=True)),
                ('contra_indications', ckeditor.fields.RichTextField(verbose_name='Противопоказания', blank=True)),
                ('side_effects', ckeditor.fields.RichTextField(verbose_name='Побочные эффекты', blank=True)),
                ('compound', ckeditor.fields.RichTextField(verbose_name='Состав', blank=True)),
                ('image', sorl.thumbnail.fields.ImageField(max_length=300, verbose_name='Изображение', null=True, blank=True, upload_to='drug')),
                ('category', mptt.fields.TreeManyToManyField(verbose_name='Категория', blank=True, db_index=True, to='main.Category')),
                ('components', models.ManyToManyField(verbose_name='Состав', blank=True, related_name='drugs', to='main.Component')),
            ],
            options={
                'abstract': False,
            },
            bases=('main.post',),
        ),
        migrations.CreateModel(
            name='DrugDosageForm',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, primary_key=True, to='main.Post')),
            ],
            options={
                'abstract': False,
            },
            bases=('main.post',),
        ),
        migrations.CreateModel(
            name='DrugUsageArea',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, primary_key=True, to='main.Post')),
            ],
            options={
                'abstract': False,
            },
            bases=('main.post',),
        ),
        migrations.AddField(
            model_name='history',
            name='post',
            field=models.ForeignKey(related_name='history_post', to='main.Post'),
        ),
        migrations.AddField(
            model_name='history',
            name='user',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True, related_name='history_user'),
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(related_name='comments', to='main.Post'),
        ),
        migrations.AddField(
            model_name='comment',
            name='updater',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True, related_name='updated_comments'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True, related_name='comments'),
        ),
        migrations.AddField(
            model_name='drug',
            name='dosage_forms',
            field=models.ManyToManyField(verbose_name='Формы выпуска', to='main.DrugDosageForm'),
        ),
        migrations.AddField(
            model_name='drug',
            name='usage_areas',
            field=models.ManyToManyField(verbose_name='Область применения', to='main.DrugUsageArea'),
        ),
        migrations.AddField(
            model_name='cosmetics',
            name='dosage_forms',
            field=models.ManyToManyField(verbose_name='Формы выпуска', to='main.CosmeticsDosageForm'),
        ),
        migrations.AddField(
            model_name='cosmetics',
            name='line',
            field=models.ForeignKey(null=True, verbose_name='Линейка', blank=True, to='main.CosmeticsLine'),
        ),
        migrations.AddField(
            model_name='cosmetics',
            name='usage_areas',
            field=models.ManyToManyField(verbose_name='Область применения', to='main.CosmeticsUsageArea'),
        ),
        migrations.AddField(
            model_name='blog',
            name='category',
            field=mptt.fields.TreeManyToManyField(verbose_name='Категория', db_index=True, to='main.Category'),
        ),
    ]
