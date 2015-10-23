# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import mptt.fields
import ckeditor_uploader.fields
import ckeditor.fields
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(db_index=True, verbose_name='Время создания', blank=True)),
                ('updated', models.DateTimeField(db_index=True, verbose_name='Время изменения', blank=True, null=True)),
                ('published', models.DateTimeField(db_index=True, verbose_name='Время публикации', blank=True, null=True)),
                ('username', models.CharField(verbose_name='Имя', max_length=256)),
                ('email', models.EmailField(verbose_name='E-Mail', max_length=254)),
                ('post_mark', models.IntegerField(verbose_name='Оценка', blank=True, null=True, choices=[(1, '1'), (1, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('body', models.TextField(verbose_name='Сообщение')),
                ('ip', models.CharField(db_index=True, max_length=15)),
                ('session_key', models.TextField(db_index=True, blank=True)),
                ('consult_required', models.BooleanField(db_index=True, verbose_name='Нужна консультация провизора', default=False)),
                ('status', models.IntegerField(db_index=True, verbose_name='Статус', choices=[(1, 'На согласовании'), (2, 'Опубликован')])),
                ('key', models.CharField(max_length=128, blank=True)),
                ('confirmed', models.BooleanField(db_index=True, default=False)),
                ('old_id', models.PositiveIntegerField(blank=True, null=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, related_name='children', to='prozdo_main.Comment')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(db_index=True, verbose_name='Время создания', blank=True)),
                ('updated', models.DateTimeField(db_index=True, verbose_name='Время изменения', blank=True, null=True)),
                ('history_type', models.IntegerField(db_index=True, choices=[(1, 'Комментарий создан'), (2, 'Комментарий сохранен'), (3, 'Комментарий оценен'), (4, 'Материал создан'), (5, 'Материал сохранен'), (6, 'Материал оценен'), (7, 'Жалоба на комментарий')])),
                ('user_points', models.PositiveIntegerField(blank=True, default=0)),
                ('ip', models.CharField(db_index=True, max_length=15, blank=True, null=True)),
                ('session_key', models.TextField(db_index=True, blank=True)),
                ('mark', models.IntegerField(verbose_name='Оценка', blank=True, null=True, choices=[(1, '1'), (1, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('old_id', models.PositiveIntegerField(blank=True, null=True)),
                ('author', models.ForeignKey(blank=True, null=True, related_name='history_author', to=settings.AUTH_USER_MODEL)),
                ('comment', models.ForeignKey(blank=True, null=True, related_name='history_comment', to='prozdo_main.Comment')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Mail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(db_index=True, verbose_name='Время создания', blank=True)),
                ('updated', models.DateTimeField(db_index=True, verbose_name='Время изменения', blank=True, null=True)),
                ('mail_type', models.PositiveIntegerField(db_index=True, choices=[(1, 'Подтверждение отзыва'), (2, 'Регистрация пользователя'), (1, 'Сброс пароля'), (4, 'Ответ на отзыв')])),
                ('subject', models.TextField()),
                ('body_html', models.TextField(blank=True, default='')),
                ('body_text', models.TextField(blank=True, default='')),
                ('email', models.EmailField(db_index=True, max_length=254)),
                ('ip', models.CharField(db_index=True, max_length=15, blank=True, null=True)),
                ('session_key', models.TextField(db_index=True, blank=True, null=True)),
                ('email_from', models.EmailField(db_index=True, max_length=254)),
                ('entity_id', models.CharField(db_index=True, max_length=20, blank=True)),
                ('user', models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(db_index=True, verbose_name='Время создания', blank=True)),
                ('updated', models.DateTimeField(db_index=True, verbose_name='Время изменения', blank=True, null=True)),
                ('title', models.CharField(db_index=True, verbose_name='Название', max_length=500)),
                ('published', models.DateTimeField(db_index=True, verbose_name='Время публикации', blank=True, null=True)),
                ('alias', models.CharField(db_index=True, verbose_name='Синоним', max_length=800, blank=True)),
                ('post_type', models.IntegerField(db_index=True, verbose_name='Вид записи', choices=[(1, 'Препарат'), (2, 'Блог'), (3, 'Форум'), (5, 'Компонент'), (4, 'Косметика'), (6, 'Бренд'), (7, 'Форма выпуска препарата'), (8, 'Форма выпуска косметики'), (9, 'Линия косметики'), (10, 'Область применения косметики'), (11, 'Област применения препарата'), (12, 'Категория')])),
                ('status', models.IntegerField(db_index=True, verbose_name='Статус', default=1, choices=[(1, 'Проект'), (2, 'Опубликован')])),
                ('old_id', models.PositiveIntegerField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(db_index=True, verbose_name='Время создания', blank=True)),
                ('updated', models.DateTimeField(db_index=True, verbose_name='Время изменения', blank=True, null=True)),
                ('role', models.PositiveIntegerField(db_index=True, blank=True, default=1, choices=[(1, 'Обычный пользователь'), (2, 'Автор'), (3, 'Врач'), (33, 'Админ')])),
                ('image', sorl.thumbnail.fields.ImageField(verbose_name='Изображение', blank=True, null=True, upload_to='user_profile')),
                ('receive_messages', models.BooleanField(db_index=True, verbose_name='Получать e-mail сообщения с сайта', default=True)),
                ('old_id', models.PositiveIntegerField(blank=True, null=True)),
                ('user', models.OneToOneField(related_name='user_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('post_ptr', models.OneToOneField(primary_key=True, to='prozdo_main.Post', parent_link=True, auto_created=True, serialize=False)),
                ('short_body', models.TextField(verbose_name='Анонс', blank=True)),
                ('body', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Содержимое', blank=True)),
                ('image', sorl.thumbnail.fields.ImageField(verbose_name='Изображение', blank=True, null=True, upload_to='blog')),
            ],
            options={
                'ordering': ('-created',),
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('post_ptr', models.OneToOneField(primary_key=True, to='prozdo_main.Post', parent_link=True, auto_created=True, serialize=False)),
            ],
            options={
                'abstract': False,
                'ordering': ('title',),
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('post_ptr', models.OneToOneField(primary_key=True, to='prozdo_main.Post', parent_link=True, auto_created=True, serialize=False)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, related_name='children', to='prozdo_main.Category')),
            ],
            options={
                'abstract': False,
                'ordering': ('title',),
            },
            bases=('prozdo_main.post', models.Model),
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('post_ptr', models.OneToOneField(primary_key=True, to='prozdo_main.Post', parent_link=True, auto_created=True, serialize=False)),
                ('body', ckeditor.fields.RichTextField(verbose_name='Содержимое', blank=True)),
                ('component_type', models.IntegerField(db_index=True, verbose_name='Тип компонента', choices=[(1, 'Витамин'), (2, 'Минеральное вещество'), (3, 'Растение'), (4, 'Прочее')])),
            ],
            options={
                'abstract': False,
                'ordering': ('title',),
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Cosmetics',
            fields=[
                ('post_ptr', models.OneToOneField(primary_key=True, to='prozdo_main.Post', parent_link=True, auto_created=True, serialize=False)),
                ('body', ckeditor.fields.RichTextField(verbose_name='Содержимое', blank=True)),
                ('image', sorl.thumbnail.fields.ImageField(verbose_name='Изображение', blank=True, null=True, upload_to='cosmetics')),
                ('brand', models.ForeignKey(verbose_name='Бренд', to='prozdo_main.Brand')),
            ],
            options={
                'abstract': False,
                'ordering': ('title',),
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='CosmeticsDosageForm',
            fields=[
                ('post_ptr', models.OneToOneField(primary_key=True, to='prozdo_main.Post', parent_link=True, auto_created=True, serialize=False)),
            ],
            options={
                'abstract': False,
                'ordering': ('title',),
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='CosmeticsLine',
            fields=[
                ('post_ptr', models.OneToOneField(primary_key=True, to='prozdo_main.Post', parent_link=True, auto_created=True, serialize=False)),
            ],
            options={
                'abstract': False,
                'ordering': ('title',),
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='CosmeticsUsageArea',
            fields=[
                ('post_ptr', models.OneToOneField(primary_key=True, to='prozdo_main.Post', parent_link=True, auto_created=True, serialize=False)),
            ],
            options={
                'abstract': False,
                'ordering': ('title',),
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Drug',
            fields=[
                ('post_ptr', models.OneToOneField(primary_key=True, to='prozdo_main.Post', parent_link=True, auto_created=True, serialize=False)),
                ('body', ckeditor.fields.RichTextField(verbose_name='Описание', blank=True)),
                ('features', ckeditor.fields.RichTextField(verbose_name='Особенности', blank=True)),
                ('indications', ckeditor.fields.RichTextField(verbose_name='Показания', blank=True)),
                ('application_scheme', ckeditor.fields.RichTextField(verbose_name='Схема приема', blank=True)),
                ('dosage_form', ckeditor.fields.RichTextField(verbose_name='Формы выпуска', blank=True)),
                ('contra_indications', ckeditor.fields.RichTextField(verbose_name='Противопоказания', blank=True)),
                ('side_effects', ckeditor.fields.RichTextField(verbose_name='Побочные эффекты', blank=True)),
                ('compound', ckeditor.fields.RichTextField(verbose_name='Состав', blank=True)),
                ('image', sorl.thumbnail.fields.ImageField(verbose_name='Изображение', blank=True, null=True, upload_to='drug')),
                ('category', mptt.fields.TreeManyToManyField(db_index=True, verbose_name='Категория', blank=True, to='prozdo_main.Category')),
                ('components', models.ManyToManyField(verbose_name='Состав', blank=True, related_name='drugs', to='prozdo_main.Component')),
            ],
            options={
                'abstract': False,
                'ordering': ('title',),
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='DrugDosageForm',
            fields=[
                ('post_ptr', models.OneToOneField(primary_key=True, to='prozdo_main.Post', parent_link=True, auto_created=True, serialize=False)),
            ],
            options={
                'abstract': False,
                'ordering': ('title',),
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='DrugUsageArea',
            fields=[
                ('post_ptr', models.OneToOneField(primary_key=True, to='prozdo_main.Post', parent_link=True, auto_created=True, serialize=False)),
            ],
            options={
                'abstract': False,
                'ordering': ('title',),
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
            field=models.ForeignKey(blank=True, null=True, related_name='history_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(to='prozdo_main.Post', related_name='comments'),
        ),
        migrations.AddField(
            model_name='comment',
            name='updater',
            field=models.ForeignKey(blank=True, null=True, related_name='updated_comments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(blank=True, null=True, related_name='comments', to=settings.AUTH_USER_MODEL),
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
            field=models.ForeignKey(verbose_name='Линейка', blank=True, null=True, to='prozdo_main.CosmeticsLine'),
        ),
        migrations.AddField(
            model_name='cosmetics',
            name='usage_areas',
            field=models.ManyToManyField(verbose_name='Область применения', to='prozdo_main.CosmeticsUsageArea'),
        ),
        migrations.AddField(
            model_name='blog',
            name='category',
            field=mptt.fields.TreeManyToManyField(db_index=True, verbose_name='Категория', to='prozdo_main.Category'),
        ),
    ]
