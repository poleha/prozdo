# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor_uploader.fields
import ckeditor.fields
import mptt.fields
import sorl.thumbnail.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('created', models.DateTimeField(verbose_name='Время создания', db_index=True, blank=True)),
                ('updated', models.DateTimeField(null=True, verbose_name='Время изменения', blank=True, db_index=True)),
                ('published', models.DateTimeField(null=True, verbose_name='Время публикации', blank=True, db_index=True)),
                ('username', models.CharField(verbose_name='Имя', max_length=256)),
                ('email', models.EmailField(verbose_name='E-Mail', max_length=254)),
                ('post_mark', models.IntegerField(null=True, verbose_name='Оценка', blank=True, choices=[(1, '1'), (1, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('body', models.TextField(verbose_name='Сообщение')),
                ('ip', models.CharField(db_index=True, max_length=300)),
                ('session_key', models.TextField(null=True, db_index=True, blank=True)),
                ('consult_required', models.BooleanField(verbose_name='Нужна консультация провизора', db_index=True, default=False)),
                ('status', models.IntegerField(verbose_name='Статус', db_index=True, choices=[(1, 'На согласовании'), (2, 'Опубликован')])),
                ('key', models.CharField(max_length=128, blank=True)),
                ('confirmed', models.BooleanField(db_index=True, default=False)),
                ('old_id', models.PositiveIntegerField(null=True, blank=True)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(null=True, blank=True, related_name='children', to='prozdo_main.Comment')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('created', models.DateTimeField(verbose_name='Время создания', db_index=True, blank=True)),
                ('updated', models.DateTimeField(null=True, verbose_name='Время изменения', blank=True, db_index=True)),
                ('history_type', models.IntegerField(db_index=True, choices=[(1, 'Комментарий создан'), (2, 'Комментарий сохранен'), (3, 'Комментарий оценен'), (4, 'Материал создан'), (5, 'Материал сохранен'), (6, 'Материал оценен'), (7, 'Жалоба на комментарий')])),
                ('user_points', models.PositiveIntegerField(default=0, blank=True)),
                ('ip', models.CharField(null=True, db_index=True, max_length=300, blank=True)),
                ('session_key', models.TextField(null=True, db_index=True, blank=True)),
                ('mark', models.IntegerField(null=True, verbose_name='Оценка', blank=True, choices=[(1, '1'), (1, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('old_id', models.PositiveIntegerField(null=True, blank=True)),
                ('deleted', models.BooleanField(verbose_name='Удалена', db_index=True, default=False)),
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('created', models.DateTimeField(verbose_name='Время создания', db_index=True, blank=True)),
                ('updated', models.DateTimeField(null=True, verbose_name='Время изменения', blank=True, db_index=True)),
                ('mail_type', models.PositiveIntegerField(db_index=True, choices=[(1, 'Подтверждение отзыва'), (2, 'Регистрация пользователя'), (1, 'Сброс пароля'), (4, 'Ответ на отзыв')])),
                ('subject', models.TextField()),
                ('body_html', models.TextField(default='', blank=True)),
                ('body_text', models.TextField(default='', blank=True)),
                ('email', models.EmailField(db_index=True, max_length=254)),
                ('ip', models.CharField(null=True, db_index=True, max_length=300, blank=True)),
                ('session_key', models.TextField(null=True, db_index=True, blank=True)),
                ('email_from', models.EmailField(db_index=True, max_length=254)),
                ('entity_id', models.CharField(db_index=True, max_length=20, blank=True)),
                ('user', models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('created', models.DateTimeField(verbose_name='Время создания', db_index=True, blank=True)),
                ('updated', models.DateTimeField(null=True, verbose_name='Время изменения', blank=True, db_index=True)),
                ('title', models.CharField(verbose_name='Название', db_index=True, max_length=500)),
                ('published', models.DateTimeField(null=True, verbose_name='Время публикации', blank=True, db_index=True)),
                ('alias', models.CharField(verbose_name='Синоним', db_index=True, max_length=800, blank=True)),
                ('post_type', models.IntegerField(verbose_name='Вид записи', db_index=True, choices=[(1, 'Препарат'), (2, 'Блог'), (3, 'Форум'), (5, 'Компонент'), (4, 'Косметика'), (6, 'Бренд'), (7, 'Форма выпуска препарата'), (8, 'Форма выпуска косметики'), (9, 'Линия косметики'), (10, 'Область применения косметики'), (11, 'Област применения препарата'), (12, 'Категория')])),
                ('status', models.IntegerField(verbose_name='Статус', db_index=True, default=1, choices=[(1, 'Проект'), (2, 'Опубликован')])),
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('created', models.DateTimeField(verbose_name='Время создания', db_index=True, blank=True)),
                ('updated', models.DateTimeField(null=True, verbose_name='Время изменения', blank=True, db_index=True)),
                ('role', models.PositiveIntegerField(db_index=True, default=1, blank=True, choices=[(1, 'Обычный пользователь'), (2, 'Автор'), (3, 'Врач'), (33, 'Админ')])),
                ('image', sorl.thumbnail.fields.ImageField(null=True, verbose_name='Изображение', upload_to='user_profile', blank=True)),
                ('receive_messages', models.BooleanField(verbose_name='Получать e-mail сообщения с сайта', db_index=True, default=True)),
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
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='prozdo_main.Post', primary_key=True, serialize=False)),
                ('short_body', models.TextField(verbose_name='Анонс', blank=True)),
                ('body', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Содержимое', blank=True)),
                ('image', sorl.thumbnail.fields.ImageField(null=True, verbose_name='Изображение', max_length=300, upload_to='blog', blank=True)),
            ],
            options={
                'ordering': ('-created',),
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='prozdo_main.Post', primary_key=True, serialize=False)),
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
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='prozdo_main.Post', primary_key=True, serialize=False)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(null=True, blank=True, related_name='children', to='prozdo_main.Category')),
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
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='prozdo_main.Post', primary_key=True, serialize=False)),
                ('body', ckeditor.fields.RichTextField(verbose_name='Содержимое', blank=True)),
                ('component_type', models.IntegerField(verbose_name='Тип компонента', db_index=True, choices=[(1, 'Витамин'), (2, 'Минеральное вещество'), (3, 'Растение'), (4, 'Прочее')])),
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
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='prozdo_main.Post', primary_key=True, serialize=False)),
                ('body', ckeditor.fields.RichTextField(verbose_name='Содержимое', blank=True)),
                ('image', sorl.thumbnail.fields.ImageField(null=True, verbose_name='Изображение', max_length=300, upload_to='cosmetics', blank=True)),
                ('brand', models.ForeignKey(verbose_name='Бренд', to='prozdo_main.Brand')),
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
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='prozdo_main.Post', primary_key=True, serialize=False)),
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
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='prozdo_main.Post', primary_key=True, serialize=False)),
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
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='prozdo_main.Post', primary_key=True, serialize=False)),
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
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='prozdo_main.Post', primary_key=True, serialize=False)),
                ('body', ckeditor.fields.RichTextField(verbose_name='Описание', blank=True)),
                ('features', ckeditor.fields.RichTextField(verbose_name='Особенности', blank=True)),
                ('indications', ckeditor.fields.RichTextField(verbose_name='Показания', blank=True)),
                ('application_scheme', ckeditor.fields.RichTextField(verbose_name='Схема приема', blank=True)),
                ('dosage_form', ckeditor.fields.RichTextField(verbose_name='Формы выпуска', blank=True)),
                ('contra_indications', ckeditor.fields.RichTextField(verbose_name='Противопоказания', blank=True)),
                ('side_effects', ckeditor.fields.RichTextField(verbose_name='Побочные эффекты', blank=True)),
                ('compound', ckeditor.fields.RichTextField(verbose_name='Состав', blank=True)),
                ('image', sorl.thumbnail.fields.ImageField(null=True, verbose_name='Изображение', max_length=300, upload_to='drug', blank=True)),
                ('category', mptt.fields.TreeManyToManyField(verbose_name='Категория', db_index=True, blank=True, to='prozdo_main.Category')),
                ('components', models.ManyToManyField(verbose_name='Состав', to='prozdo_main.Component', blank=True, related_name='drugs')),
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
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='prozdo_main.Post', primary_key=True, serialize=False)),
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
                ('post_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='prozdo_main.Post', primary_key=True, serialize=False)),
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
            field=models.ForeignKey(null=True, blank=True, to='prozdo_main.CosmeticsLine', verbose_name='Линейка'),
        ),
        migrations.AddField(
            model_name='cosmetics',
            name='usage_areas',
            field=models.ManyToManyField(verbose_name='Область применения', to='prozdo_main.CosmeticsUsageArea'),
        ),
        migrations.AddField(
            model_name='blog',
            name='category',
            field=mptt.fields.TreeManyToManyField(verbose_name='Категория', db_index=True, to='prozdo_main.Category'),
        ),
    ]
