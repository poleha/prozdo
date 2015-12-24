# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor.fields
import ckeditor_uploader.fields
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
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('created', models.DateTimeField(verbose_name='Время создания', db_index=True, blank=True)),
                ('updated', models.DateTimeField(verbose_name='Время изменения', null=True, db_index=True, blank=True)),
                ('published', models.DateTimeField(verbose_name='Время публикации', null=True, db_index=True, blank=True)),
                ('username', models.CharField(verbose_name='Имя', max_length=256)),
                ('email', models.EmailField(verbose_name='E-Mail', max_length=254)),
                ('post_mark', models.IntegerField(verbose_name='Оценка', null=True, blank=True, choices=[(1, '1'), (1, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('body', models.TextField(verbose_name='Сообщение')),
                ('ip', models.CharField(db_index=True, max_length=300)),
                ('session_key', models.TextField(null=True, db_index=True, blank=True)),
                ('consult_required', models.BooleanField(default=False, verbose_name='Нужна консультация провизора', db_index=True)),
                ('status', models.IntegerField(verbose_name='Статус', db_index=True, choices=[(1, 'На согласовании'), (2, 'Опубликован')])),
                ('key', models.CharField(blank=True, max_length=128)),
                ('confirmed', models.BooleanField(default=False, db_index=True)),
                ('old_id', models.PositiveIntegerField(null=True, blank=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(to='main.Comment', null=True, related_name='children', blank=True)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('created', models.DateTimeField(verbose_name='Время создания', db_index=True, blank=True)),
                ('updated', models.DateTimeField(verbose_name='Время изменения', null=True, db_index=True, blank=True)),
                ('history_type', models.IntegerField(db_index=True, choices=[(1, 'Комментарий создан'), (2, 'Комментарий сохранен'), (3, 'Комментарий оценен'), (4, 'Материал создан'), (5, 'Материал сохранен'), (6, 'Материал оценен'), (7, 'Жалоба на комментарий')])),
                ('user_points', models.PositiveIntegerField(default=0, blank=True)),
                ('ip', models.CharField(null=True, db_index=True, blank=True, max_length=300)),
                ('session_key', models.TextField(null=True, db_index=True, blank=True)),
                ('mark', models.IntegerField(verbose_name='Оценка', null=True, blank=True, choices=[(1, '1'), (1, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('old_id', models.PositiveIntegerField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False, verbose_name='Удалена', db_index=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, related_name='history_author', blank=True)),
                ('comment', models.ForeignKey(to='main.Comment', null=True, related_name='history_comment', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Mail',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('created', models.DateTimeField(verbose_name='Время создания', db_index=True, blank=True)),
                ('updated', models.DateTimeField(verbose_name='Время изменения', null=True, db_index=True, blank=True)),
                ('mail_type', models.PositiveIntegerField(db_index=True, choices=[(1, 'Подтверждение отзыва'), (2, 'Регистрация пользователя'), (1, 'Сброс пароля'), (4, 'Ответ на отзыв')])),
                ('subject', models.TextField()),
                ('body_html', models.TextField(default='', blank=True)),
                ('body_text', models.TextField(default='', blank=True)),
                ('email', models.EmailField(db_index=True, max_length=254)),
                ('ip', models.CharField(null=True, db_index=True, blank=True, max_length=300)),
                ('session_key', models.TextField(null=True, db_index=True, blank=True)),
                ('email_from', models.EmailField(db_index=True, max_length=254)),
                ('entity_id', models.CharField(db_index=True, blank=True, max_length=20)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('created', models.DateTimeField(verbose_name='Время создания', db_index=True, blank=True)),
                ('updated', models.DateTimeField(verbose_name='Время изменения', null=True, db_index=True, blank=True)),
                ('title', models.CharField(verbose_name='Название', db_index=True, max_length=500)),
                ('published', models.DateTimeField(verbose_name='Время публикации', null=True, db_index=True, blank=True)),
                ('alias', models.CharField(verbose_name='Синоним', db_index=True, blank=True, max_length=800)),
                ('post_type', models.IntegerField(verbose_name='Вид записи', db_index=True, choices=[(1, 'Препарат'), (2, 'Блог'), (3, 'Форум'), (5, 'Компонент'), (4, 'Косметика'), (6, 'Бренд'), (7, 'Форма выпуска препарата'), (8, 'Форма выпуска косметики'), (9, 'Линия косметики'), (10, 'Область применения косметики'), (11, 'Област применения препарата'), (12, 'Категория')])),
                ('status', models.IntegerField(default=1, verbose_name='Статус', db_index=True, choices=[(1, 'Проект'), (2, 'Опубликован')])),
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
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('created', models.DateTimeField(verbose_name='Время создания', db_index=True, blank=True)),
                ('updated', models.DateTimeField(verbose_name='Время изменения', null=True, db_index=True, blank=True)),
                ('role', models.PositiveIntegerField(default=1, db_index=True, blank=True, choices=[(1, 'Обычный пользователь'), (2, 'Автор'), (3, 'Врач'), (33, 'Админ')])),
                ('image', sorl.thumbnail.fields.ImageField(verbose_name='Изображение', null=True, upload_to='user_profile', blank=True)),
                ('receive_messages', models.BooleanField(default=True, verbose_name='Получать e-mail сообщения с сайта', db_index=True)),
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
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, to='main.Post', parent_link=True)),
                ('short_body', models.TextField(verbose_name='Анонс', blank=True)),
                ('body', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Содержимое', blank=True)),
                ('image', sorl.thumbnail.fields.ImageField(verbose_name='Изображение', null=True, upload_to='blog', blank=True, max_length=300)),
            ],
            options={
                'ordering': ('-created',),
            },
            bases=('main.post',),
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, to='main.Post', parent_link=True)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('main.post',),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, to='main.Post', parent_link=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(to='main.Category', null=True, related_name='children', blank=True)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('main.post', models.Model),
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, to='main.Post', parent_link=True)),
                ('body', ckeditor.fields.RichTextField(verbose_name='Содержимое', blank=True)),
                ('component_type', models.IntegerField(verbose_name='Тип компонента', db_index=True, choices=[(1, 'Витамин'), (2, 'Минеральное вещество'), (3, 'Растение'), (4, 'Прочее')])),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('main.post',),
        ),
        migrations.CreateModel(
            name='Cosmetics',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, to='main.Post', parent_link=True)),
                ('body', ckeditor.fields.RichTextField(verbose_name='Содержимое', blank=True)),
                ('image', sorl.thumbnail.fields.ImageField(verbose_name='Изображение', null=True, upload_to='cosmetics', blank=True, max_length=300)),
                ('brand', models.ForeignKey(to='main.Brand', verbose_name='Бренд')),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('main.post',),
        ),
        migrations.CreateModel(
            name='CosmeticsDosageForm',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, to='main.Post', parent_link=True)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('main.post',),
        ),
        migrations.CreateModel(
            name='CosmeticsLine',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, to='main.Post', parent_link=True)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('main.post',),
        ),
        migrations.CreateModel(
            name='CosmeticsUsageArea',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, to='main.Post', parent_link=True)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('main.post',),
        ),
        migrations.CreateModel(
            name='Drug',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, to='main.Post', parent_link=True)),
                ('body', ckeditor.fields.RichTextField(verbose_name='Описание', blank=True)),
                ('features', ckeditor.fields.RichTextField(verbose_name='Особенности', blank=True)),
                ('indications', ckeditor.fields.RichTextField(verbose_name='Показания', blank=True)),
                ('application_scheme', ckeditor.fields.RichTextField(verbose_name='Схема приема', blank=True)),
                ('dosage_form', ckeditor.fields.RichTextField(verbose_name='Формы выпуска', blank=True)),
                ('contra_indications', ckeditor.fields.RichTextField(verbose_name='Противопоказания', blank=True)),
                ('side_effects', ckeditor.fields.RichTextField(verbose_name='Побочные эффекты', blank=True)),
                ('compound', ckeditor.fields.RichTextField(verbose_name='Состав', blank=True)),
                ('image', sorl.thumbnail.fields.ImageField(verbose_name='Изображение', null=True, upload_to='drug', blank=True, max_length=300)),
                ('category', mptt.fields.TreeManyToManyField(verbose_name='Категория', db_index=True, blank=True, to='main.Category')),
                ('components', models.ManyToManyField(verbose_name='Состав', related_name='drugs', blank=True, to='main.Component')),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('main.post',),
        ),
        migrations.CreateModel(
            name='DrugDosageForm',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, to='main.Post', parent_link=True)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('main.post',),
        ),
        migrations.CreateModel(
            name='DrugUsageArea',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, to='main.Post', parent_link=True)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('main.post',),
        ),
        migrations.AddField(
            model_name='history',
            name='post',
            field=models.ForeignKey(to='main.Post', related_name='history_post'),
        ),
        migrations.AddField(
            model_name='history',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, related_name='history_user', blank=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(to='main.Post', related_name='comments'),
        ),
        migrations.AddField(
            model_name='comment',
            name='updater',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, related_name='updated_comments', blank=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, related_name='comments', blank=True),
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
            field=models.ForeignKey(to='main.CosmeticsLine', null=True, verbose_name='Линейка', blank=True),
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
