from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from django.db.models.signals import post_save, pre_save
from . import helper
from django.core.exceptions import ValidationError
from django.db.models.aggregates import Sum, Count
#from multi_image_upload.models import MyImageField
from django.conf import settings
from math import ceil
from django.core.urlresolvers import reverse
from mptt.models import MPTTModel, TreeForeignKey, TreeManager
from mptt.querysets import TreeQuerySet
from mptt.fields import TreeManyToManyField
from django.utils import timezone
from allauth.account.models import EmailAddress, EmailConfirmation
from sorl.thumbnail import ImageField, get_thumbnail
import re
from django.utils.html import strip_tags
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.db.models import Q
#from django.contrib.contenttypes.fields import GenericForeignKey
#from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from cacheops.query import ManagerMixin
from cacheops import invalidate_obj, invalidate_model, invalidate_all
from django.core.mail.message import EmailMultiAlternatives
from django.utils import timezone
from django.template.loader import render_to_string


#<Constants***********************************************************

POST_TYPE_DRUG = 1
POST_TYPE_BLOG = 2
POST_TYPE_FORUM = 3
POST_TYPE_COSMETICS = 4
POST_TYPE_COMPONENT = 5
POST_TYPE_BRAND = 6
POST_TYPE_DRUG_DOSAGE_FORM = 7
POST_TYPE_COSMETICS_DOSAGE_FORM = 8
POST_TYPE_COSMETICS_LINE = 9
POST_TYPE_COSMETICS_USAGE_AREA = 10
POST_TYPE_DRUG_USAGE_AREA = 11
POST_TYPE_CATEGORY = 12


POST_TYPES = (
    (POST_TYPE_DRUG, 'Препарат'),
    (POST_TYPE_BLOG, 'Блог'),
    (POST_TYPE_FORUM, 'Форум'),
    (POST_TYPE_COMPONENT, 'Компонент'),
    (POST_TYPE_COSMETICS, 'Косметика'),
    (POST_TYPE_BRAND, 'Бренд'),
    (POST_TYPE_DRUG_DOSAGE_FORM, 'Форма выпуска препарата'),
    (POST_TYPE_COSMETICS_DOSAGE_FORM, 'Форма выпуска косметики'),
    (POST_TYPE_COSMETICS_LINE, 'Линия косметики'),
    (POST_TYPE_COSMETICS_USAGE_AREA, 'Область применения косметики'),
    (POST_TYPE_DRUG_USAGE_AREA, 'Област применения препарата'),
    (POST_TYPE_CATEGORY, 'Категория'),
)

USER_ROLE_REGULAR = 1
USER_ROLE_AUTHOR = 2
USER_ROLE_DOCTOR = 3
USER_ROLE_ADMIN = 33

USER_ROLES = (
    (USER_ROLE_REGULAR, 'Обычный пользователь'),
    (USER_ROLE_AUTHOR, 'Автор'),
    (USER_ROLE_DOCTOR, 'Врач'),
    (USER_ROLE_ADMIN, 'Админ'),
)


POST_MARKS_FOR_COMMENT = (
    (1, '1'),
    (1, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
)

COMMENT_STATUS_PENDING_APPROVAL = 1
COMMENT_STATUS_PUBLISHED = 2

COMMENT_STATUSES = (
    (COMMENT_STATUS_PENDING_APPROVAL, 'На согласовании'),
    (COMMENT_STATUS_PUBLISHED, 'Опубликован'),
)


POST_STATUS_PROJECT = 1
POST_STATUS_PUBLISHED = 2


POST_STATUSES = (
    (POST_STATUS_PROJECT, 'Проект'),
    (POST_STATUS_PUBLISHED, 'Опубликован'),
)


COMPONENT_TYPE_VITAMIN = 1
COMPONENT_TYPE_MINERAL = 2
COMPONENT_TYPE_PLANT = 3
COMPONENT_TYPE_OTHER = 4
COMPONENT_TYPES = (
    (COMPONENT_TYPE_VITAMIN, 'Витамин'),
    (COMPONENT_TYPE_MINERAL, 'Минеральное вещество'),
    (COMPONENT_TYPE_PLANT, 'Растение'),
    (COMPONENT_TYPE_OTHER, 'Прочее'),
)


#Constants>***********************************************************

#<Posts******************************************************************
#TODO move it to cache
EMPTY_CACHE_PLACEHOLDER = '__EMPTY__'

CACHED_ATTRIBUTE_KEY_TEMPLATE = '_cached_{0}-{1}-{2}'

class CachedProperty(property):
    pass

def cached_property(func):
    @CachedProperty
    def wrapper(self):
        if settings.PROZDO_CACHE_ENABLED:
            key = CACHED_ATTRIBUTE_KEY_TEMPLATE.format(type(self).__name__, func.__name__, self.pk)
            res = cache.get(key)
            if res is None:
                res = func(self)
                if res is None:
                    res = EMPTY_CACHE_PLACEHOLDER
                cache.set(key, res, settings.PROZDO_CACHED_ATTRIBUTE_DURATION)
            if res == EMPTY_CACHE_PLACEHOLDER:
                res = None
            return res
        else:
            return func(self)
    return wrapper

CACHED_METHOD_SHORT_KEY_TEMPLATE = '_cached_method_{0}_{1}'
CACHED_METHOD_KEY_TEMPLATE = CACHED_METHOD_SHORT_KEY_TEMPLATE + '_{2}_{3}'

"""
class cached_method:
    def __init__(self, func):
        self.func = func

    #TODO make it module aware
    def generate_cache_key(self, *args, **kwargs):
        instance = args[0]
        args = args[1:]
        name = type(instance).__name__
        pk = instance.pk
        return CACHED_METHOD_KEY_TEMPLATE.format(name, pk, str(args), str(kwargs))

    def __call__(self, *args, **kwargs):
        if not settings.PROZDO_CACHE_ENABLED:
            return self.func(*args, **kwargs)
        key = self.generate_cache_key(*args, **kwargs)
        res = cache.get(key)
        if res is None:
            res = self.func(*args, **kwargs)
            cache.set(key, res, settings.PROZDO_CACHED_ATTRIBUTE_DURATION)
        return res

    def __get__(self, instance, owner):
        def wrapper(*args, **kwargs):
            return self(instance, *args, **kwargs)
        return wrapper
"""

class CachedModelMixin(models.Model):
    class Meta:
        abstract = True

    cache_key_template = CACHED_ATTRIBUTE_KEY_TEMPLATE

    def get_cache_key(self, attr_name):
        return self.cache_key_template.format(type(self).__name__, attr_name, self.pk)

    #def get_cached(self, attr_name):
    #    if settings.PROZDO_CACHE_ENABLED:
    #        key = self.get_cache_key(attr_name)
    #        res = cache.get(key)
    #        if res is None:
    #            res = getattr(self, attr_name)
    #            if res is None:
    #                res = EMPTY_CACHE_PLACEHOLDER
    #            cache.set(key, res, settings.PROZDO_CACHED_ATTRIBUTE_DURATION)
    #        if res == EMPTY_CACHE_PLACEHOLDER:
    #            res = None
    #    else:
    #        res = getattr(self, attr_name)
    #    return res

    def invalidate_cache(self, attr_name):
        if settings.PROZDO_CACHE_ENABLED:
            key = self.get_cache_key(attr_name)
            cache.delete(key)
            res = getattr(self, attr_name)
            if res is None:
                res = EMPTY_CACHE_PLACEHOLDER
            cache.set(key, res, settings.PROZDO_CACHED_ATTRIBUTE_DURATION)

    #TODO make only if instance key attr is instance of models.Model
    def full_invalidate_cache(self):
        if settings.PROZDO_CACHE_ENABLED:
            #instance_keys = tuple((field.name for field in self._meta.fields))
            prop_keys = []
            for c in type(self).mro():
                prop_keys += [k for k, v in c.__dict__.items() if isinstance(v, CachedProperty)]

            for attr_name in set(prop_keys):
                self.invalidate_cache(attr_name)

    def clean_cache(self, attr_name):
        if settings.PROZDO_CACHE_ENABLED:
            key = self.get_cache_key(attr_name)
            cache.delete(key)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if settings.PROZDO_CACHE_ENABLED:
            self.full_invalidate_cache()

    #TODO
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)


class SuperModel(CachedModelMixin):
    created = models.DateTimeField(blank=True, verbose_name='Время создания', db_index=True)
    updated = models.DateTimeField(blank=True, null=True, verbose_name='Время изменения', db_index=True)

    class Meta:
        abstract = True

    @property
    def saved_version(self):
        if self.pk:
            try:
                saved_version = type(self).objects.get(pk=self.pk)
            except:
                saved_version = None
        else:
            saved_version = None
        return saved_version

    def save(self, *args, **kwargs):
        if not self.pk and not self.created:
            self.created = timezone.now()
        if self.pk and not self.updated:
            self.updated = timezone.now()
        super().save(*args, **kwargs)

class AbstractModel(SuperModel):
    class Meta:
        abstract = True
        ordering = ('title', )
    title = models.CharField(max_length=500, verbose_name='Название', db_index=True)

    def __str__(self):
        return self.title


def class_with_published_mixin(published_status):
    class PublishedModelMixin(models.Model):
        class Meta:
            abstract = True

        published = models.DateTimeField(null=True, blank=True, verbose_name='Время публикации', db_index=True)
        def save(self, *args, **kwargs):
            if self.status == published_status and not self.published:
                self.published = timezone.now()
            super().save(*args, **kwargs)
    return PublishedModelMixin


class PostQueryset(models.QuerySet):
    def get_available(self):
        queryset = self.filter(status=POST_STATUS_PUBLISHED)
        return queryset


class PostManager(models.manager.BaseManager.from_queryset(PostQueryset), ManagerMixin):
    use_for_related_fields = True

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset



class Post(AbstractModel, class_with_published_mixin(POST_STATUS_PUBLISHED)):
    alias = models.CharField(max_length=800, blank=True, verbose_name='Синоним', db_index=True)
    post_type = models.IntegerField(choices=POST_TYPES, verbose_name='Вид записи', db_index=True )
    status = models.IntegerField(choices=POST_STATUSES, verbose_name='Статус', default=POST_STATUS_PROJECT, db_index=True)
    old_id = models.PositiveIntegerField(null=True, blank=True)
    objects = PostManager()

    @classmethod
    def get_post_type(cls):
        if cls == Drug:
            return POST_TYPE_DRUG
        elif cls == Blog:
            return POST_TYPE_BLOG
        #elif cls == Forum:
        #    return POST_TYPE_FORUM
        elif cls == Component:
            return POST_TYPE_COMPONENT
        elif cls == Cosmetics:
            return POST_TYPE_COSMETICS
        elif cls == Brand:
            return POST_TYPE_BRAND
        elif cls == DrugDosageForm:
            return POST_TYPE_DRUG_DOSAGE_FORM
        elif cls == CosmeticsDosageForm:
            return POST_TYPE_COSMETICS_DOSAGE_FORM
        elif cls == CosmeticsLine:
            return POST_TYPE_COSMETICS_LINE
        elif cls == CosmeticsUsageArea:
            return POST_TYPE_COSMETICS_USAGE_AREA
        elif cls == DrugUsageArea:
            return POST_TYPE_DRUG_USAGE_AREA
        elif cls == Category:
            return POST_TYPE_CATEGORY

    @property
    def is_drug(self):
        return self.post_type == POST_TYPE_DRUG

    @property
    def is_blog(self):
        return self.post_type == POST_TYPE_BLOG

    @property
    def is_forum(self):
        return self.post_type == POST_TYPE_FORUM

    @property
    def is_component(self):
        return self.post_type == POST_TYPE_COMPONENT

    @property
    def is_cosmetics(self):
        return self.post_type == POST_TYPE_COSMETICS


    @classmethod
    def list_view_default_template(cls):
        if cls == Component:
            return 'prozdo_main/post/_component_list.html'
        else:
            return 'prozdo_main/post/_post_list_grid.html'

    @classmethod
    def ajax_submit_url(cls):
        if cls == Drug:
            return reverse('drug-list-ajax')
        elif cls == Blog:
            return reverse('blog-list-ajax')
        elif cls == Cosmetics:
            return reverse('cosmetics-list-ajax')
        elif cls == Component:
            return reverse('component-list-ajax')

    @classmethod
    def submit_url(cls):
        if cls == Drug:
            return reverse('drug-list')
        elif cls == Blog:
            return reverse('blog-list')
        elif cls == Cosmetics:
            return reverse('cosmetics-list')
        elif cls == Component:
            return reverse('component-list')


    @classmethod
    def get_list_url(cls):
        if cls == Component:
            return reverse('component-list')
        elif cls == Drug:
            return reverse('drug-list')
        elif cls == Blog:
            return reverse('blog-list')
        elif cls == Cosmetics:
            return reverse('cosmetics-list')


    @property
    def update_url(self):
        if self.is_drug:
            return reverse('drug-update', kwargs={'pk': self.pk})
        elif self.is_blog:
            return reverse('blog-update', kwargs={'pk': self.pk})
        if self.is_component:
            return reverse('component-update', kwargs={'pk': self.pk})
        elif self.is_cosmetics:
            return reverse('cosmetics-update', kwargs={'pk': self.pk})
        elif self.is_forum:
            return reverse('forum-update', kwargs={'pk': self.pk})

    #Вообще неправильно и все это надо(как и get_post_type) делать в каждом дочернем классе. Но так удобнее...
    @property
    def show_body_label(self):
        if self.is_drug:
            return True
        else:
            return False

    @property
    def obj(self):
        if self.post_type == POST_TYPE_DRUG:
            return self.drug
        elif self.post_type == POST_TYPE_COMPONENT:
            return self.component
        elif self.post_type == POST_TYPE_BLOG:
            return self.blog
        elif self.post_type == POST_TYPE_FORUM:
            return self.forum
        elif self.post_type == POST_TYPE_COSMETICS:
            return self.cosmetics
        elif self.post_type == POST_TYPE_BRAND:
            return self.brand
        elif self.post_type == POST_TYPE_DRUG_DOSAGE_FORM:
            return self.drug_dosage_form
        elif self.post_type == POST_TYPE_COSMETICS_DOSAGE_FORM:
            return self.cosmetics_dosage_form
        elif self.post_type == POST_TYPE_COSMETICS_LINE:
            return self.cosmetics_line
        elif self.post_type == POST_TYPE_COSMETICS_USAGE_AREA:
            return self.cosmetics_usage_area
        elif self.post_type == POST_TYPE_DRUG_USAGE_AREA:
            return self.drug_usage_area
        elif self.post_type == POST_TYPE_CATEGORY:
            return self.category

    #@cached_property
    #def _cached_get_absolute_url(self):
    #    alias = self.alias
    #    if alias:
    #        return reverse('post-detail-alias', kwargs={'alias': alias})
    #    else:
    #        return reverse('post-detail-pk', kwargs={'pk': self.pk})

    def get_absolute_url(self):
        alias = self.alias
        if alias:
            return reverse('post-detail-alias', kwargs={'alias': alias})
        else:
            return reverse('post-detail-pk', kwargs={'pk': self.pk})

    def get_mark_by_request(self, request):
        user = request.user
        if user.is_authenticated():
            try:
                mark = History.objects.get(user=user, history_type=HISTORY_TYPE_POST_RATED, post=self).mark
            except:
                mark = ''
        else:
            try:
                mark = History.objects.get(session_key=request.session._get_or_create_session_key(), history_type=HISTORY_TYPE_POST_RATED, user=None).mark
            except:
                mark = 0

        return mark

    @cached_property
    def average_mark(self):
        try:
            mark = History.objects.filter(post=self).aggregate(Sum('mark'))['mark__sum']
            if mark is None:
                mark = 0
        except:
            mark = 0

        if mark > 0 and self.marks_count > 0:
            return round(mark / self.marks_count, 2)
        else:
            return 0

    @cached_property
    def marks_count(self):
        try:
            count = History.objects.filter(post=self, history_type=HISTORY_TYPE_POST_RATED).aggregate(Count('mark'))['mark__count']
            if count is None:
                count = 0
        except:
            count = 0
        return count

    @cached_property
    def published_comments_count(self):
        return self.comments.get_available().count()

    @cached_property
    def last_comment_date(self):
        try:
            last_comment = self.comments.get_available().latest('created')
            date = last_comment.created
        except:
            date = None
        return date


    def make_alias(self):
        return helper.make_alias(self.title)

    def clean(self):
        if self.alias:
            try:
                self.alias.encode('ascii')
            except:
                raise ValidationError('Недопустимые символы в синониме {0}'.format(self.alias))

            result = re.match('[a-z0-9_\-]{1,}', self.alias)
            if not result:
                raise ValidationError('Недопустимые символы в синониме')

    def save(self, *args, **kwargs):
        self.clean()
        self.title = helper.trim_title(self.title)
        #saved_version = self.saved_version
        if hasattr(self, 'title') and self.title and not self.alias:
            self.alias = self.make_alias()
        if self.alias:
            alias_is_busy = Post.objects.filter(alias=self.alias).exclude(pk=self.pk)
            if alias_is_busy:
                raise ValidationError('Синоним {0} занят'.format(self.alias))

        self.post_type = self.get_post_type()
        super().save(*args, **kwargs)
        History.save_history(history_type=HISTORY_TYPE_POST_CREATED, post=self)

    """
    @cached_property
    def first_level_available_comments_created_dec(self):
        return self.comments.filter(status=COMMENT_STATUS_PUBLISHED, parent_id=None).order_by('-created')

    @cached_property
    def first_level_available_comments_created_inc(self):
        return self.comments.filter(status=COMMENT_STATUS_PUBLISHED, parent_id=None).order_by('created')


    @cached_property
    def available_comments_created_dec(self):
        return self.comments.filter(status=COMMENT_STATUS_PUBLISHED).order_by('-created')

    @cached_property
    def available_comments_created_inc(self):
        return self.comments.filter(status=COMMENT_STATUS_PUBLISHED).order_by('created')
    """


class Brand(Post):
    def get_absolute_url(self):
        return "{0}?brands={1}".format(reverse('cosmetics-list'), self.pk)

    def make_alias(self):
        return ''

class DrugDosageForm(Post):
    def get_absolute_url(self):
        return "{0}?dosage_forms={1}".format(reverse('drug-list'), self.pk)

    def make_alias(self):
        return ''


class CosmeticsDosageForm(Post):
    def get_absolute_url(self):
        return "{0}?dosage_forms={1}".format(reverse('cosmetics-list'), self.pk)

    def make_alias(self):
        return ''


class CosmeticsLine(Post):
    def get_absolute_url(self):
        return "{0}?lines={1}".format(reverse('cosmetics-list'), self.pk)

    def make_alias(self):
        return ''

class CosmeticsUsageArea(Post):
    def get_absolute_url(self):
        return "{0}?usage_areas={1}".format(reverse('cosmetics-list'), self.pk)

    def make_alias(self):
        return ''


class DrugUsageArea(Post):
    def get_absolute_url(self):
        return "{0}?usage_areas={1}".format(reverse('drug-list'), self.pk)

    def make_alias(self):
        return ''




class Category(Post, MPTTModel):  #Для блога
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    objects = TreeManager()

    def make_alias(self):
        return ''


class Component(Post):
    body = RichTextField(verbose_name='Содержимое', blank=True)
    component_type = models.IntegerField(choices=COMPONENT_TYPES, verbose_name='Тип компонента')
    objects = PostManager()

    @property
    def component_type_text(self):
        for component_type in COMPONENT_TYPES:
            if self.component_type == component_type[0]:
                return component_type[1]


class Drug(Post):
    body = RichTextField(verbose_name='Описание', blank=True)
    features = RichTextField(verbose_name='Особенности', blank=True)
    indications = RichTextField(verbose_name='Показания', blank=True)
    application_scheme = RichTextField(verbose_name='Схема приема', blank=True)
    dosage_form = RichTextField(verbose_name='Формы выпуска', blank=True)
    contra_indications = RichTextField(verbose_name='Противопоказания', blank=True)
    side_effects = RichTextField(verbose_name='Побочные эффекты', blank=True)
    compound = RichTextField(verbose_name='Состав', blank=True)
    image = ImageField(verbose_name='Изображение', upload_to='drug', blank=True, null=True)

    dosage_forms = models.ManyToManyField(DrugDosageForm, verbose_name='Формы выпуска')
    usage_areas = models.ManyToManyField(DrugUsageArea, verbose_name='Область применения')
    components = models.ManyToManyField(Component, verbose_name='Состав', blank=True, related_name='drugs')
    category = TreeManyToManyField(Category, verbose_name='Категория', blank=True)
    objects = PostManager()

    @property
    def thumb110(self):
        try:
            return get_thumbnail(self.image, '110x200', quality=99).url
        except:
            return ''

    @property
    def thumb150(self):
        try:
            return get_thumbnail(self.image, '150x300', quality=99).url
        except:
            return ''

    @property
    def thumb220(self):
        try:
            return get_thumbnail(self.image, '220x400', quality=99).url
        except:
            return ''

class Cosmetics(Post):
    body = RichTextField(verbose_name='Содержимое', blank=True)
    image = ImageField(verbose_name='Изображение', upload_to='cosmetics', blank=True, null=True)

    brand = models.ForeignKey(Brand, verbose_name='Бренд')
    line = models.ForeignKey(CosmeticsLine, verbose_name='Линейка', null=True, blank=True)
    dosage_forms = models.ManyToManyField(CosmeticsDosageForm, verbose_name='Формы выпуска')
    usage_areas = models.ManyToManyField(CosmeticsUsageArea, verbose_name='Область применения')
    objects = PostManager()

    #TODO проверить, убрать лишнее
    @property
    def thumb110(self):
        try:
            return get_thumbnail(self.image, '110x200', quality=99).url
        except:
            return ''

    @property
    def thumb150(self):
        try:
            return get_thumbnail(self.image, '150x300', quality=99).url
        except:
            return ''

    @property
    def thumb220(self):
        try:
            return get_thumbnail(self.image, '220x400', quality=99).url
        except:
            return ''



class Blog(Post):
    class Meta:
        ordering = ('-created', )
    short_body = models.TextField(verbose_name='Анонс', blank=True)
    body = RichTextUploadingField(verbose_name='Содержимое', blank=True)
    image = ImageField(verbose_name='Изображение', upload_to='blog', blank=True, null=True)
    category = TreeManyToManyField(Category, verbose_name='Категория')
    objects = PostManager()


    @property
    def thumb110(self):
        try:
            return get_thumbnail(self.image, '110x200', quality=99).url
        except:
            return ''

    @property
    def thumb150(self):
        try:
            return get_thumbnail(self.image, '150x300', quality=99).url
        except:
            return ''

    @property
    def thumb220(self):
        try:
            return get_thumbnail(self.image, '220x400', quality=99).url
        except:
            return ''

    @property
    def thumb360(self):
        try:
            return get_thumbnail(self.image, '360x720', quality=99).url
        except:
            return ''

    @property
    def anons(self):
        if self.short_body:
            return self.short_body
        else:
            return helper.cut_text(strip_tags(self.body), 200)

    @cached_property
    def mark(self):
        try:
            mark = History.objects.filter(post=self, history_type=HISTORY_TYPE_POST_RATED).aggregate(Count('pk'))['pk__count']
            if mark is None:
                mark = 0
        except:
            mark = 0
        return mark

    def get_mark_blog_by_request(self, request):
        user = request.user
        if user.is_authenticated():
            try:
                mark = History.objects.filter(user=user, history_type=HISTORY_TYPE_POST_RATED, post=self).count()
            except:
                mark = 0
        else:
            try:
                mark = History.objects.filter(post=self, history_type=HISTORY_TYPE_POST_RATED, user=None).filter(session_key=request.session._get_or_create_session_key()).count()
            except:
                mark = 0

        return mark

#class Forum(Post):
#    body = models.TextField(verbose_name='Содержимое', blank=True)


#Post>*******************************************************************



class CommentTreeQueryset(TreeQuerySet):
    def get_available(self):
        queryset = self.filter(status=COMMENT_STATUS_PUBLISHED)
        return queryset


class CommentManager(models.manager.BaseManager.from_queryset(CommentTreeQueryset), ManagerMixin):
    use_for_related_fields = True



class Comment(SuperModel, MPTTModel, class_with_published_mixin(COMMENT_STATUS_PUBLISHED)):
    class Meta:
        ordering = ['-created']
    post = models.ForeignKey(Post, related_name='comments')
    username = models.CharField(max_length=256, verbose_name='Имя')
    email = models.EmailField(verbose_name='E-Mail')
    post_mark = models.IntegerField(choices=POST_MARKS_FOR_COMMENT, blank=True, null=True, verbose_name='Оценка')
    body = models.TextField(verbose_name='Сообщение')
    user = models.ForeignKey(User, null=True, blank=True, related_name='comments')
    ip = models.CharField(max_length=15, db_index=True)
    session_key = models.TextField(blank=True, db_index=True)
    consult_required = models.BooleanField(default=False, verbose_name='Нужна консультация провизора', db_index=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    status = models.IntegerField(choices=COMMENT_STATUSES, verbose_name='Статус', db_index=True)
    updater = models.ForeignKey(User, null=True, blank=True, related_name='updated_comments')
    key = models.CharField(max_length=128, blank=True)
    confirmed = models.BooleanField(default=False, db_index=True)
    old_id = models.PositiveIntegerField(null=True, blank=True)

    objects = CommentManager()

    def __str__(self):
        return self.short_body

    @cached_property
    def has_avaliable_children(self):
        return self.children.get_available().exists()


    @property
    def get_tree_level(self):
        if hasattr(self, 'tree_level'):
            return self.tree_level
        else:
            return 0

    @property
    def consult_done(self):
        return self.available_children.filter(user__user_profile__role=USER_ROLE_DOCTOR).exists()

    @property
    def update_url(self):
            return reverse('comment-update', kwargs={'pk': self.pk})


    @cached_property
    def get_children_tree(self):
        return self._get_children_tree()

    def _get_children_tree(self, cur=None, level=1):
        tree = []
        if cur is None:
            cur = self
        else:
            tree.append(cur)
        for child in cur.children.get_available().order_by('created'):
            child.tree_level = level
            tree += child._get_children_tree(child, level+1)
        return tree

    @property
    def page(self):
        comments = self.post.comments.get_available().order_by('-created')
        #count = comments.count()
        #pages_count = ceil(count / page_size)
        page_size = settings.POST_COMMENTS_PAGE_SIZE
        comments_tuple = tuple(comments)
        try:
            index = comments_tuple.index(self) + 1
            current_page = ceil(index / page_size)
        except:
            current_page = 1
        return current_page


    def send_answer_to_comment_message(self):
        user = self.parent.user
        if user.user_profile.receive_messages and not self.user == self.parent.user:
            email_to = user.email

            email_sent = Mail.objects.filter(mail_type=MAIL_TYPE_ANSWER_TO_COMMENT,
                                                     entity_id=self.pk,
                                                     user=user).exists()
            if email_sent:
                return False

            txt_template_name = 'prozdo_main/comment/email/answer_to_comment.txt'
            html_template_name = 'prozdo_main/comment/email/answer_to_comment.html'

            text = render_to_string(txt_template_name, {'comment': self, 'site_url': settings.SITE_URL})
            html = render_to_string(html_template_name, {'comment': self, 'site_url': settings.SITE_URL})

            subject = 'Получен ответ на Ваш отзыв на Prozdo.ru'
            from_email = settings.DEFAULT_FROM_EMAIL

            try:
                msg = EmailMultiAlternatives(subject, text, from_email, [email_to])
                msg.attach_alternative(html, "text/html")
                res = msg.send()
                if res:
                    Mail.objects.create(
                                mail_type=MAIL_TYPE_ANSWER_TO_COMMENT,
                                user=user if user.is_authenticated() else None,
                                subject=subject,
                                body_html=html,
                                body_text=text,
                                email=email_to,
                                ip=self.ip,
                                session_key=self.session_key,
                                entity_id=self.pk,
                                email_from=from_email,
                            )
                    return True

            except:
                pass


    def send_confirmation_mail(self, user=None, request=None):
        if not user and request:
            user = request.user
        if request:
            ip = helper.get_client_ip(request)
            session_key = request.session._get_or_create_session_key()
        else:
            ip = None
            session_key = None

        confirm_comment_text_template_name = 'prozdo_main/comment/email/confirm_comment_html_template.html'
        confirm_comment_html_template_name = 'prozdo_main/comment/email/confirm_comment_text_template.txt'
        if not user.email_confirmed and not self.confirmed:
                html = render_to_string(confirm_comment_html_template_name, {'comment': self, 'site_url': settings.SITE_URL})
                text = render_to_string(confirm_comment_text_template_name, {'comment': self, 'site_url': settings.SITE_URL})
                subject = 'Вы оставили отзыв на {}'.format('Prozdo.ru')
                from_email = settings.DEFAULT_FROM_EMAIL
                to = self.email
                try:
                    msg = EmailMultiAlternatives(subject, text, from_email, [to])
                    msg.attach_alternative(html, "text/html")
                    res = msg.send()
                    if res:
                        Mail.objects.create(
                            mail_type=MAIL_TYPE_COMMENT_CONFIRM,
                            user=user if user.is_authenticated() else None,
                            subject=subject,
                            body_html=html,
                            body_text=text,
                            email=to,
                            ip=ip,
                            session_key=session_key,
                            entity_id=self.pk,
                            email_from=from_email,
                        )
                except:
                    pass

    @cached_property
    def available_children(self):
        return self.get_descendants().filter(status=COMMENT_STATUS_PUBLISHED)


    @cached_property
    def available_children_count(self):
        return self.available_children.count()


    @property
    def short_body(self):
        return helper.cut_text(self.body)


    @cached_property
    def comment_mark(self):
        try:
            mark = History.objects.filter(comment=self, history_type=HISTORY_TYPE_COMMENT_RATED).aggregate(Count('pk'))['pk__count']
            if mark is None:
                mark = 0
        except:
            mark = 0
        return mark


    @cached_property
    def _cached_get_absolute_url(self):
        if self.status == COMMENT_STATUS_PUBLISHED:
            return '{0}/comment/{1}#c{1}'.format(self.post.get_absolute_url(), self.pk)
        else:
            return self.post.get_absolute_url()

    def get_absolute_url(self):
        return self._cached_get_absolute_url

    def get_confirm_url(self):
        return settings.SITE_URL + reverse('comment-confirm', kwargs={'comment_pk': self.pk, 'key': self.key})


    def get_status(self):
        if self.user and self.user.user_profile.can_publish_comment():
            return COMMENT_STATUS_PUBLISHED
        else:
            if helper.comment_body_ok(self.body) and helper.comment_author_ok(self.username):
                return COMMENT_STATUS_PUBLISHED
            else:
                return COMMENT_STATUS_PENDING_APPROVAL

    @cached_property
    def complain_count(self):
        try:
            count = History.objects.filter(comment=self, history_type=HISTORY_TYPE_COMMENT_COMPLAINT).aggregate(Count('pk'))['pk__count']
            if count is None:
                count = 0
        except:
            count = 0
        return count

    def generate_key(self):
        if self.key:
            return self.key
        else:
            return helper.generate_key(128)

    def save(self, *args, **kwargs):
        if not self.confirmed:
            if self.user and self.user.email_confirmed:
                self.confirmed = True

        if not self.key:
            self.key = self.generate_key()

        if not self.user or not(self.user.is_admin or self.user.is_doctor or self.user.is_author):
            self.body = strip_tags(self.body)


        super().save(*args, **kwargs)
        History.save_history(history_type=HISTORY_TYPE_COMMENT_CREATED, post=self.post, comment=self, ip=self.ip, session_key=self.session_key, user=self.user)

        if self.status == COMMENT_STATUS_PUBLISHED and self.parent and self.parent.confirmed and self.parent.user:
            self.send_answer_to_comment_message()


    def delete(self, *args, **kwargs):
        post = self.post
        user = self.user
        ancestors = self.get_ancestors()
        descendants = self.get_descendants()
        super().delete(*args, **kwargs)
        if post:
            post.obj.full_invalidate_cache()
        if user:
            user.user_profile.full_invalidate_cache()
        for ancestor in ancestors:
            ancestor.full_invalidate_cache()
            invalidate_obj(ancestor)
        for descendant in descendants:
            descendant.full_invalidate_cache()
            invalidate_obj(descendant)



    #******************
    def hist_exists_by_comment_and_user(self, history_type, user):
        return History.objects.filter(history_type=history_type, comment=self, user=user).exists()

    def hist_exists_by_request(self, history_type, request):
        user = request.user
        if user and user.is_authenticated():
            hist_exists = self.hist_exists_by_comment_and_user(history_type, user)
        else:
            session_key = request.session._get_or_create_session_key()
            if session_key is None:
                return False
            hist_exists = History.exists_by_comment(session_key, self, history_type)
        return hist_exists

    def show_do_action_button(self, history_type, request):
        return not self.hist_exists_by_request(history_type, request) and not self.is_author_for_show_buttons(request)

    def show_undo_action_button(self, history_type, request):
        return self.hist_exists_by_request(history_type, request) and not self.is_author_for_show_buttons(request)

    def is_author_for_show_buttons(self, request):
        user = request.user
        if user and user.is_authenticated():
            return user == self.user
        else:
            session_key = request.session._get_or_create_session_key()
            return self.session_key == session_key

    #******************

    def hist_exists_by_data(self, history_type, user=None, ip=None, session_key=None):
        if user and user.is_authenticated():
            hist_exists = History.objects.filter(history_type=history_type, comment=self, user=user).exists()
        else:
            if session_key:
                hist_exists_by_key = History.objects.filter(history_type=history_type, comment=self, session_key=session_key).exists()
            else:
                hist_exists_by_key = False
            if ip:
                hist_exists_by_ip = History.objects.filter(history_type=history_type, comment=self, ip=ip).exists()
            else:
                hist_exists_by_ip = False
            hist_exists = hist_exists_by_key or hist_exists_by_ip

        return hist_exists


    def can_do_action(self, history_type, user, ip, session_key):
        return not self.hist_exists_by_data(history_type, user, ip, session_key) and not self.is_author_for_save_history(user, ip, session_key)

    #def can_undo_action(self, history_type, user, session_key):
    #    return self.hist_exists_by_data(history_type=history_type, user=user, session_key=session_key) and not self.is_author_for_save_history(user=user, session_key=session_key)

    def is_author_for_save_history(self, user=None, ip=None, session_key=None):
        if user and user.is_authenticated():
            return user == self.user
        else:
            return self.session_key == session_key or self.ip == ip

    #******************



HISTORY_TYPE_COMMENT_CREATED = 1
HISTORY_TYPE_COMMENT_SAVED = 2
HISTORY_TYPE_COMMENT_RATED = 3
HISTORY_TYPE_POST_CREATED = 4
HISTORY_TYPE_POST_SAVED = 5
HISTORY_TYPE_POST_RATED = 6
HISTORY_TYPE_COMMENT_COMPLAINT = 7
#HISTORY_TYPE_POST_COMPLAINT = 8
#HISTORY_TYPE_BLOG_RATED = 8

HISTORY_TYPES = (
    (HISTORY_TYPE_COMMENT_CREATED, 'Комментарий создан'),
    (HISTORY_TYPE_COMMENT_SAVED, 'Комментарий сохранен'),
    (HISTORY_TYPE_COMMENT_RATED, 'Комментарий оценен'),
    (HISTORY_TYPE_POST_CREATED, 'Материал создан'),
    (HISTORY_TYPE_POST_SAVED, 'Материал сохранен'),
    (HISTORY_TYPE_POST_RATED, 'Материал оценен'),
    (HISTORY_TYPE_COMMENT_COMPLAINT, 'Жалоба на комментарий'),
    #(HISTORY_TYPE_POST_COMPLAINT, 'Жалоба на материал'),
    #(HISTORY_TYPE_BLOG_RATED, 'Запись блога оценена'),

)

HISTORY_TYPES_POINTS = {
HISTORY_TYPE_COMMENT_CREATED: 3,
HISTORY_TYPE_COMMENT_SAVED: 0,
HISTORY_TYPE_COMMENT_RATED: 1,
HISTORY_TYPE_POST_CREATED: 0,
HISTORY_TYPE_POST_SAVED: 0,
HISTORY_TYPE_POST_RATED: 1,
HISTORY_TYPE_COMMENT_COMPLAINT: 0,
#HISTORY_TYPE_BLOG_RATED: 0,
}


class History(SuperModel):
    post = models.ForeignKey(Post, related_name='history_post')
    history_type = models.IntegerField(choices=HISTORY_TYPES, db_index=True)
    author = models.ForeignKey(User, null=True, blank=True, related_name='history_author')
    user = models.ForeignKey(User, null=True, blank=True, related_name='history_user')
    comment = models.ForeignKey(Comment, null=True, blank=True, related_name='history_comment')
    user_points = models.PositiveIntegerField(default=0, blank=True)
    #author_points = models.PositiveIntegerField(default=0, blank=True)
    ip = models.CharField(max_length=15, null=True, blank=True, db_index=True)
    session_key = models.TextField(blank=True, db_index=True)
    mark = models.IntegerField(choices=POST_MARKS_FOR_COMMENT, blank=True, null=True, verbose_name='Оценка')
    old_id = models.PositiveIntegerField(null=True, blank=True)


    @staticmethod
    def get_points(history_type):
        return HISTORY_TYPES_POINTS[history_type]

    def __str__(self):
        return "{0} - {1} - {2}".format(self.history_type, self.post, self.comment)




    @staticmethod
    def save_history(history_type, post, user=None, ip=None, session_key=None, comment=None, mark=None):
        if session_key is None:
            return None

        if hasattr(post, 'user'):
            post_author = post.user
        else:
            post_author = None

        if user and not user.is_authenticated():
            user = None

        if isinstance(mark, str):
            mark = int(mark)

        if mark is None and comment is not None and comment.post_mark:
            mark = comment.post_mark

        if history_type == HISTORY_TYPE_POST_CREATED:
            hist_exists = History.objects.filter(history_type=history_type, post=post).exists()
            if not hist_exists:
                h = History.objects.create(history_type=history_type, post=post, user=user,
                                       user_points=History.get_points(history_type), ip=ip, author=post_author, session_key=session_key)
            else:
                h = History.save_history(HISTORY_TYPE_POST_SAVED, post, user, ip, session_key, comment)
            return h
        elif history_type == HISTORY_TYPE_POST_SAVED:
            h = History.objects.create(history_type=history_type, post=post, user=user, ip=ip, author=post_author, session_key=session_key)
            return h
        elif history_type == HISTORY_TYPE_COMMENT_CREATED:
            hist_exists = History.objects.filter(history_type=history_type, comment=comment).exists()
            if not hist_exists:

                h = History.objects.create(history_type=history_type, post=post, user=user, comment=comment, ip=ip,
                                       user_points=History.get_points(history_type),
                                       author=post_author, mark=mark, session_key=session_key)
            else:
                h = History.save_history(HISTORY_TYPE_COMMENT_SAVED, post, user, ip, session_key, comment, mark=mark)
            return h
        elif history_type == HISTORY_TYPE_COMMENT_SAVED:
            h = History.objects.create(history_type=history_type, post=post, user=user, comment=comment, ip=ip,
                                   user_points=History.get_points(history_type), author=post_author, session_key=session_key)
            return h
        elif history_type in [HISTORY_TYPE_COMMENT_RATED, HISTORY_TYPE_COMMENT_COMPLAINT]:
            #if history_type == HISTORY_TYPE_COMMENT_RATED:
            #    author_points = 1
            #else:
            #    author_points = 0
            if comment.can_do_action(history_type=history_type, user=user, session_key=session_key, ip=ip):
                h = History.objects.create(history_type=history_type, post=post, user=user, comment=comment, ip=ip,
                                       user_points=History.get_points(history_type),
                                       author=comment.user, session_key=session_key)
                return h
        elif history_type == HISTORY_TYPE_POST_RATED:
            if user and user.is_authenticated():
                hist_exists = History.objects.filter(history_type=history_type, post=post, user=user).exists()
            else:
                hist_exists_by_key = History.objects.filter(history_type=history_type, post=post, session_key=session_key, user=None).exists()
                hist_exists_by_ip = History.objects.filter(history_type=history_type, post=post, ip=ip, user=None).exists()
                hist_exists = hist_exists_by_key or hist_exists_by_ip

            if not hist_exists and ((not post.is_blog and mark and mark > 0) or post.is_blog):
                h = History.objects.create(history_type=history_type, post=post, user=user, ip=ip, comment=comment,
                                   user_points=History.get_points(history_type), author=post_author, mark=mark, session_key=session_key)
                return h


    @classmethod
    def exists(cls, session_key):
        if not session_key:
            return False
        if not settings.PROZDO_CACHE_ENABLED:
            return History.objects.filter(session_key=session_key).exists()
        prefix = '_cached_history_exists_'
        key = prefix + session_key
        res = cache.get(key)
        if res is None:
            res = History.objects.filter(session_key=session_key).exists()
            cache.set(key, res, settings.HISTORY_EXISTS_DURATION)
        return res

    def invalidate_exists(self):
        if settings.PROZDO_CACHE_ENABLED:
            prefix = '_cached_history_exists_'
            key = prefix + self.session_key
            cache.delete(key)
            res = History.objects.filter(session_key=self.session_key).exists()
            cache.set(key, res, settings.HISTORY_EXISTS_DURATION)

    def delete_exists(self):
        if settings.PROZDO_CACHE_ENABLED:
            prefix = '_cached_history_exists_'
            key = prefix + self.session_key
            cache.delete(key)


    @classmethod
    def exists_by_comment(cls, session_key, comment, history_type):
        if not session_key:
            return False
        if not settings.PROZDO_CACHE_ENABLED:
            return History.objects.filter(session_key=session_key, comment=comment, history_type=history_type).exists()
        template = '_cached_history_exists_by_comment_{0}-{1}-{2}'
        key = template.format(session_key, comment.pk, history_type)
        res = cache.get(key)
        if res is None:
            res = History.objects.filter(session_key=session_key, comment=comment, history_type=history_type).exists()
            cache.set(key, res, settings.HISTORY_EXISTS_DURATION)
        return res

    def invalidate_exists_by_comment(self):
        if settings.PROZDO_CACHE_ENABLED:
            if self.comment:
                template = '_cached_history_exists_by_comment_{0}-{1}-{2}'
                key = template.format(self.session_key, self.comment.pk, self.history_type)
                cache.delete(key)
                res = History.objects.filter(session_key=self.session_key, comment=self.comment, history_type=self.history_type).exists()
                cache.set(key, res, settings.HISTORY_EXISTS_DURATION)

    def delete_exists_by_comment(self):
        if settings.PROZDO_CACHE_ENABLED:
            if self.comment:
                template = '_cached_history_exists_by_comment_{0}-{1}-{2}'
                key = template.format(self.session_key, self.comment.pk, self.history_type)
                cache.delete(key)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.comment:
            self.comment.full_invalidate_cache()
            invalidate_obj(self.comment)

            for ancestor in self.comment.get_ancestors():
                ancestor.full_invalidate_cache()
                invalidate_obj(ancestor)
            for descendant in self.comment.get_descendants():
                descendant.full_invalidate_cache()
                invalidate_obj(descendant)

        if self.post:
            self.post.obj.full_invalidate_cache()
            invalidate_obj(self.post.obj)

        if self.user:
            self.user.user_profile.full_invalidate_cache()
        if self.author:
            self.author.user_profile.full_invalidate_cache()
            invalidate_obj(self.author)
        self.invalidate_exists()
        self.invalidate_exists_by_comment()


    def delete(self, *args, **kwargs):
        post = self.post
        comment = self.comment
        user = self.user
        author = self.author
        self.delete_exists_by_comment()
        self.delete_exists()
        super().delete(*args, **kwargs)
        if comment:
            comment.full_invalidate_cache()
            invalidate_obj(comment)

            for ancestor in comment.get_ancestors():
                ancestor.full_invalidate_cache()
                invalidate_obj(ancestor)
            for descendant in comment.get_descendants():
                descendant.full_invalidate_cache()
                invalidate_obj(descendant)

        if post:
            post.obj.full_invalidate_cache()
            invalidate_obj(post.obj)
        if user:
            user.user_profile.full_invalidate_cache()
            invalidate_obj(user)
        if author:
            author.user_profile.full_invalidate_cache()
            invalidate_obj(author)


class UserProfile(SuperModel):
    # required by the auth model
    user = models.OneToOneField(User, related_name='user_profile')  # reverse returns single object, not queryset
    role = models.PositiveIntegerField(choices=USER_ROLES, default=USER_ROLE_REGULAR, blank=True)
    image = ImageField(verbose_name='Изображение', upload_to='user_profile', blank=True, null=True)
    receive_messages = models.BooleanField(default=True, verbose_name='Получать e-mail сообщения с сайта', blank=True)
    #first_name = models.CharField(max_length=800, verbose_name='Имя', blank=True)
    #last_name = models.CharField(max_length=800, verbose_name='Фамилия', blank=True)
    old_id = models.PositiveIntegerField(null=True, blank=True)


    def can_publish_comment(self):
        if self.user.is_admin or self.user.is_author or self.user.is_doctor or self.get_user_karm >= 10:
            return True
        else:
            return False

    def get_unsubscribe_url(self):
        email_adress = EmailAddress.objects.get(email=self.user.email)
        try:
            key = email_adress.emailconfirmation_set.latest('created').key
        except:
            key = EmailConfirmation.create(email_adress).key

        return reverse('unsubscribe', kwargs={'email': self.user.email, 'key': key})

    def karm_history(self):
        return self._karm_history().order_by('-created')

    def _karm_history(self):
        hists = History.objects.filter(author=self.user, history_type=HISTORY_TYPE_COMMENT_RATED)
        return hists


    def _activity_history(self):
        return History.objects.filter(user=self.user, user_points__gt=0)

    @cached_property
    def activity_history(self):
        return self._activity_history().order_by('-created')

    @cached_property
    def get_user_activity(self):
        try:
            activity = self.activity_history.aggregate(Sum('user_points'))['user_points__sum']
        except:
            activity = ''
        return activity


    @cached_property
    def get_user_karm(self):
        try:
            karm = self.karm_history().aggregate(Sum('user_points'))['user_points__sum']
        except:
            karm = 0
        return karm if karm is not None else 0


    def get_email_confirmed(self):
        return EmailAddress.objects.filter(user=self.user, verified=True, email=self.user.email).exists()



    @property
    def thumb50(self):
        try:
            return get_thumbnail(self.image, '50x50', quality=99).url
        except:
            return ''

    @property
    def thumb100(self):
        try:
            return get_thumbnail(self.image, '100x100', quality=99).url
        except:
            return ''


    def __str__(self):
        return 'Профиль пользователя {0}, pk={1}'.format(self.user.username, self.user.pk)

    @classmethod
    def get_profile(cls, user):
        user_profile, created = cls.objects.get_or_create(user=user)
        if created:
            user_profile.save()
        return user_profile

    def save(self, *args, **kwargs):
        if self.user.is_staff:
            self.role = USER_ROLE_ADMIN

        super().save(*args, **kwargs)
        invalidate_obj(self.user)



def create_user_profile(sender, instance, created, **kwargs):
    profile, created = UserProfile.objects.get_or_create(user=instance)
    if created:
        profile.save()

def confirm_user_comments(sender, instance, created, **kwargs):
    if instance.email_confirmed:
        for comment in instance.comments.filter(confirmed=False):
            comment.confirmed = True
            comment.save()

def confirm_user_comments_by_email(sender, instance, created, **kwargs):
    if instance.verified:
        for comment in instance.user.comments.filter(confirmed=False):
            comment.confirmed = True
            comment.save()


post_save.connect(create_user_profile, sender=User)
post_save.connect(confirm_user_comments, sender=User)
post_save.connect(confirm_user_comments_by_email, sender=EmailAddress)




def is_regular(self):
    if self.user_profile.role == USER_ROLE_REGULAR:
        return True
    else:
        return False

def get_user_image(self):
    return self.user_profile.image

@property
def karm_history(self):
    return self.user_profile.karm_history

@property
def activity_history(self):
    return self.user_profile.activity_history

@property
def get_user_activity(self):
    return self.user_profile.get_user_activity

@property
def get_user_karm(self):
    return self.user_profile.get_user_karm


@property
def get_email_confirmed(self):
    return self.user_profile.get_email_confirmed()

User.is_regular = property(is_regular)
User.image = property(get_user_image)
User.karm_history = karm_history
User.activity_history = activity_history
User.karm = get_user_karm
User.get_karm_url = lambda self: reverse('user-karma', kwargs={'pk': self.pk})
User.get_comments_url = lambda self: reverse('user-comments', kwargs={'pk': self.pk})
User.get_activity_url = lambda self: reverse('user-activity', kwargs={'pk': self.pk})
User.get_absolute_url = lambda self: reverse('user-detail', kwargs={'pk': self.pk})

User.activity = get_user_activity
User.email_confirmed = get_email_confirmed

User.is_admin = property(lambda self: self.user_profile.role == USER_ROLE_ADMIN)
User.is_author = property(lambda self: self.user_profile.role == USER_ROLE_AUTHOR)
User.is_regular = property(lambda self: self.user_profile.role == USER_ROLE_REGULAR)
User.is_doctor = property(lambda self: self.user_profile.role == USER_ROLE_DOCTOR)
User.thumb100 = property(lambda self: self.user_profile.thumb100)
User.thumb50 = property(lambda self: self.user_profile.thumb50)


AnonymousUser.is_regular = True
AnonymousUser.image = None
AnonymousUser.email_confirmed = False
AnonymousUser.karm = 0
AnonymousUser.activity = 0


MAIL_TYPE_COMMENT_CONFIRM = 1
MAIL_TYPE_USER_REGISTRATION = 2
MAIL_TYPE_PASSWORD_RESET = 3
MAIL_TYPE_ANSWER_TO_COMMENT = 4

MAIL_TYPES = (
    (MAIL_TYPE_COMMENT_CONFIRM, 'Подтверждение отзыва'),
    (MAIL_TYPE_USER_REGISTRATION, 'Регистрация пользователя'),
    (MAIL_TYPE_COMMENT_CONFIRM, 'Сброс пароля'),
    (MAIL_TYPE_ANSWER_TO_COMMENT, 'Ответ на отзыв'),
)

class Mail(SuperModel):
    mail_type = models.PositiveIntegerField(choices=MAIL_TYPES)
    subject = models.TextField()
    body_html=models.TextField(default='', blank=True)
    body_text=models.TextField(default='', blank=True)
    email = models.EmailField()
    user = models.ForeignKey(User, blank=True, null=True)
    ip = models.CharField(max_length=15, null=True, blank=True)
    session_key = models.TextField(null=True, blank=True)
    email_from = models.EmailField()
    entity_id = models.CharField(max_length=20, blank=True)


def request_with_empty_guest(request):
    user = request.user
    if user.is_authenticated():
        return False

    session_key = request.session._get_or_create_session_key()
    exists = History.exists(session_key)
    if not exists:
        return True

    return False







