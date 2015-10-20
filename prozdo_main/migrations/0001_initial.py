# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import ckeditor.fields
import ckeditor_uploader.fields
import sorl.thumbnail.fields
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('created', models.DateTimeField(verbose_name='Время создания', blank=True, db_index=True)),
                ('updated', models.DateTimeField(null=True, verbose_name='Время изменения', blank=True, db_index=True)),
                ('published', models.DateTimeField(null=True, verbose_name='Время публикации', blank=True, db_index=True)),
                ('username', models.CharField(verbose_name='Имя', max_length=256)),
                ('email', models.EmailField(verbose_name='E-Mail', max_length=254)),
                ('post_mark', models.IntegerField(null=True, verbose_name='Оценка', blank=True, choices=[(1, '1'), (1, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('body', models.TextField(verbose_name='Сообщение')),
                ('ip', models.CharField(max_length=15, db_index=True)),
                ('session_key', models.TextField(blank=True, db_index=True)),
                ('consult_required', models.BooleanField(verbose_name='Нужна консультация провизора', default=False, db_index=True)),
                ('status', models.IntegerField(verbose_name='Статус', db_index=True, choices=[(1, 'На согласовании'), (2, 'Опубликован')])),
                ('key', models.CharField(blank=True, max_length=128)),
                ('confirmed', models.BooleanField(default=False, db_index=True)),
                ('old_id', models.PositiveIntegerField(null=True, blank=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', null=True, to='prozdo_main.Comment', blank=True)),
            ],
            options={
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('created', models.DateTimeField(verbose_name='Время создания', blank=True, db_index=True)),
                ('updated', models.DateTimeField(null=True, verbose_name='Время изменения', blank=True, db_index=True)),
                ('history_type', models.IntegerField(db_index=True, choices=[(1, 'Комментарий создан'), (2, 'Комментарий сохранен'), (3, 'Комментарий оценен'), (4, 'Материал создан'), (5, 'Материал сохранен'), (6, 'Материал оценен'), (7, 'Жалоба на комментарий')])),
                ('user_points', models.PositiveIntegerField(default=0, blank=True)),
                ('ip', models.CharField(null=True, blank=True, max_length=15, db_index=True)),
                ('session_key', models.TextField(blank=True, db_index=True)),
                ('mark', models.IntegerField(null=True, verbose_name='Оценка', blank=True, choices=[(1, '1'), (1, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('old_id', models.PositiveIntegerField(null=True, blank=True)),
                ('author', models.ForeignKey(related_name='history_author', null=True, to=settings.AUTH_USER_MODEL, blank=True)),
                ('comment', models.ForeignKey(related_name='history_comment', null=True, to='prozdo_main.Comment', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Mail',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('created', models.DateTimeField(verbose_name='Время создания', blank=True, db_index=True)),
                ('updated', models.DateTimeField(null=True, verbose_name='Время изменения', blank=True, db_index=True)),
                ('mail_type', models.PositiveIntegerField(choices=[(1, 'Подтверждение отзыва'), (2, 'Регистрация пользователя'), (1, 'Сброс пароля'), (4, 'Ответ на отзыв')])),
                ('subject', models.TextField()),
                ('body_html', models.TextField(default='', blank=True)),
                ('body_text', models.TextField(default='', blank=True)),
                ('email', models.EmailField(max_length=254)),
                ('ip', models.CharField(null=True, blank=True, max_length=15)),
                ('session_key', models.TextField(null=True, blank=True)),
                ('email_from', models.EmailField(max_length=254)),
                ('entity_id', models.CharField(blank=True, max_length=20)),
                ('user', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('created', models.DateTimeField(verbose_name='Время создания', blank=True, db_index=True)),
                ('updated', models.DateTimeField(null=True, verbose_name='Время изменения', blank=True, db_index=True)),
                ('title', models.CharField(verbose_name='Название', max_length=500, db_index=True)),
                ('published', models.DateTimeField(null=True, verbose_name='Время публикации', blank=True, db_index=True)),
                ('alias', models.CharField(verbose_name='Синоним', blank=True, max_length=800, db_index=True)),
                ('post_type', models.IntegerField(verbose_name='Вид записи', db_index=True, choices=[(1, 'Препарат'), (2, 'Блог'), (3, 'Форум'), (5, 'Компонент'), (4, 'Косметика'), (6, 'Бренд'), (7, 'Форма выпуска препарата'), (8, 'Форма выпуска косметики'), (9, 'Линия косметики'), (10, 'Область применения косметики'), (11, 'Област применения препарата'), (12, 'Категория')])),
                ('status', models.IntegerField(verbose_name='Статус', default=1, db_index=True, choices=[(1, 'Проект'), (2, 'Опубликован')])),
                ('old_id', models.PositiveIntegerField(null=True, blank=True)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('created', models.DateTimeField(verbose_name='Время создания', blank=True, db_index=True)),
                ('updated', models.DateTimeField(null=True, verbose_name='Время изменения', blank=True, db_index=True)),
                ('role', models.PositiveIntegerField(default=1, blank=True, choices=[(1, 'Обычный пользователь'), (2, 'Автор'), (3, 'Врач'), (33, 'Админ')])),
                ('image', sorl.thumbnail.fields.ImageField(null=True, verbose_name='Изображение', blank=True, upload_to='user_profile')),
                ('receive_messages', models.BooleanField(verbose_name='Получать e-mail сообщения с сайта', default=True)),
                ('old_id', models.PositiveIntegerField(null=True, blank=True)),
                ('user', models.OneToOneField(related_name='user_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, to='prozdo_main.Post', parent_link=True, serialize=False, primary_key=True)),
                ('short_body', models.TextField(verbose_name='Анонс', blank=True)),
                ('body', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Содержимое', blank=True)),
                ('image', sorl.thumbnail.fields.ImageField(null=True, verbose_name='Изображение', blank=True, upload_to='blog')),
            ],
            options={
                'ordering': ('-created',),
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, to='prozdo_main.Post', parent_link=True, serialize=False, primary_key=True)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, to='prozdo_main.Post', parent_link=True, serialize=False, primary_key=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', null=True, to='prozdo_main.Category', blank=True)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('prozdo_main.post', models.Model),
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, to='prozdo_main.Post', parent_link=True, serialize=False, primary_key=True)),
                ('body', ckeditor.fields.RichTextField(verbose_name='Содержимое', blank=True)),
                ('component_type', models.IntegerField(verbose_name='Тип компонента', choices=[(1, 'Витамин'), (2, 'Минеральное вещество'), (3, 'Растение'), (4, 'Прочее')])),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Cosmetics',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, to='prozdo_main.Post', parent_link=True, serialize=False, primary_key=True)),
                ('body', ckeditor.fields.RichTextField(verbose_name='Содержимое', blank=True)),
                ('image', sorl.thumbnail.fields.ImageField(null=True, verbose_name='Изображение', blank=True, upload_to='cosmetics')),
                ('brand', models.ForeignKey(to='prozdo_main.Brand', verbose_name='Бренд')),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='CosmeticsDosageForm',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, to='prozdo_main.Post', parent_link=True, serialize=False, primary_key=True)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='CosmeticsLine',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, to='prozdo_main.Post', parent_link=True, serialize=False, primary_key=True)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='CosmeticsUsageArea',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, to='prozdo_main.Post', parent_link=True, serialize=False, primary_key=True)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Drug',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, to='prozdo_main.Post', parent_link=True, serialize=False, primary_key=True)),
                ('body', ckeditor.fields.RichTextField(verbose_name='Описание', blank=True)),
                ('features', ckeditor.fields.RichTextField(verbose_name='Особенности', blank=True)),
                ('indications', ckeditor.fields.RichTextField(verbose_name='Показания', blank=True)),
                ('application_scheme', ckeditor.fields.RichTextField(verbose_name='Схема приема', blank=True)),
                ('dosage_form', ckeditor.fields.RichTextField(verbose_name='Формы выпуска', blank=True)),
                ('contra_indications', ckeditor.fields.RichTextField(verbose_name='Противопоказания', blank=True)),
                ('side_effects', ckeditor.fields.RichTextField(verbose_name='Побочные эффекты', blank=True)),
                ('compound', ckeditor.fields.RichTextField(verbose_name='Состав', blank=True)),
                ('image', sorl.thumbnail.fields.ImageField(null=True, verbose_name='Изображение', blank=True, upload_to='drug')),
                ('category', mptt.fields.TreeManyToManyField(to='prozdo_main.Category', verbose_name='Категория', blank=True)),
                ('components', models.ManyToManyField(to='prozdo_main.Component', related_name='drugs', verbose_name='Состав', blank=True)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='DrugDosageForm',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, to='prozdo_main.Post', parent_link=True, serialize=False, primary_key=True)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='DrugUsageArea',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, to='prozdo_main.Post', parent_link=True, serialize=False, primary_key=True)),
            ],
            options={
                'ordering': ('title',),
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
            field=models.ForeignKey(related_name='history_user', null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(to='prozdo_main.Post', related_name='comments'),
        ),
        migrations.AddField(
            model_name='comment',
            name='updater',
            field=models.ForeignKey(related_name='updated_comments', null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(related_name='comments', null=True, to=settings.AUTH_USER_MODEL, blank=True),
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
            field=models.ForeignKey(null=True, to='prozdo_main.CosmeticsLine', verbose_name='Линейка', blank=True),
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
