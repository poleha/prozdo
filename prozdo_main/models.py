from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from django.db.models.signals import post_save, pre_save
from .helper import make_alias, get_client_ip, cut_text, comment_body_ok, comment_author_ok, generate_key, trim_title
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
from allauth.account.models import EmailAddress
from django.template.loader import render_to_string
from django.core.mail.message import EmailMultiAlternatives
from sorl.thumbnail import ImageField, get_thumbnail
import re
from django.utils.html import strip_tags
#from django.contrib.contenttypes.fields import GenericForeignKey
#from django.contrib.contenttypes.models import ContentType

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



class SuperModel(models.Model):
    created = models.DateTimeField(blank=True)
    updated = models.DateTimeField(blank=True, null=True)

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
    title = models.CharField(max_length=500, verbose_name='Название')

    def __str__(self):
        return self.title


def class_with_published_mixin(published_status):
    class PublishedModelMixin(models.Model):
        class Meta:
            abstract = True

        published = models.DateTimeField(null=True, blank=True, verbose_name='Время публикации')

        def save(self, *args, **kwargs):
            if self.status == published_status and not self.published:
                self.published = timezone.now()
            super().save(*args, **kwargs)
    return PublishedModelMixin


class PostQueryset(models.QuerySet):
    def get_available(self):
        queryset = self.filter(status=POST_STATUS_PUBLISHED)
        return queryset


class PostManager(models.manager.BaseManager.from_queryset(PostQueryset)):
    use_for_related_fields = True

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset



class Post(AbstractModel, class_with_published_mixin(POST_STATUS_PUBLISHED)):
    alias = models.CharField(max_length=800, blank=True, verbose_name='Синоним')
    post_type = models.IntegerField(choices=POST_TYPES, verbose_name='Вид записи')
    status = models.IntegerField(choices=POST_STATUSES, verbose_name='Статус', default=POST_STATUS_PROJECT)
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
                mark = History.objects.get(ip=get_client_ip(request), history_type=HISTORY_TYPE_POST_RATED, user=None).mark
            except:
                mark = ''
        return mark

    @property
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

    @property
    def marks_count(self):
        try:
            count = History.objects.filter(post=self, history_type=HISTORY_TYPE_POST_RATED).aggregate(Count('mark'))['mark__count']
            if count is None:
                count = 0
        except:
            count = 0
        return count

    @property
    def published_comments_count(self):
        return self.comments.get_available().count()

    @property
    def last_comment_date(self):
        try:
            last_comment = self.comments.get_available().latest('created')
            date = last_comment.created
        except:
            date = None
        return date


    def make_alias(self):
        return make_alias(self.title)

    def clean(self):
        if self.alias:
            try:
                self.alias.encode('ascii')
            except:
                raise ValidationError('Недопустимые символы в синониме')

            result = re.match('[a-z0-9_\-]{1,}', self.alias)
            if not result:
                raise ValidationError('Недопустимые символы в синониме')

    def save(self, *args, **kwargs):
        self.clean()
        self.title = trim_title(self.title)
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
    body = models.TextField(verbose_name='Содержимое', blank=True)
    component_type = models.IntegerField(choices=COMPONENT_TYPES, verbose_name='Тип компонента')
    objects = PostManager()

    @property
    def component_type_text(self):
        for component_type in COMPONENT_TYPES:
            if self.component_type == component_type[0]:
                return component_type[1]


class Drug(Post):
    body = models.TextField(verbose_name='Описание', blank=True)
    features = models.TextField(verbose_name='Особенности', blank=True)
    indications = models.TextField(verbose_name='Показания', blank=True)
    application_scheme = models.TextField(verbose_name='Схема приема', blank=True)
    dosage_form = models.TextField(verbose_name='Формы выпуска', blank=True)
    contra_indications = models.TextField(verbose_name='Противопоказания', blank=True)
    side_effects = models.TextField(verbose_name='Побочные эффекты', blank=True)
    compound = models.TextField(verbose_name='Состав', blank=True)
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
    body = models.TextField(verbose_name='Содержимое', blank=True)
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
    body = models.TextField(verbose_name='Содержимое', blank=True)
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
            return cut_text(strip_tags(self.body), 200)



#class Forum(Post):
#    body = models.TextField(verbose_name='Содержимое', blank=True)


#Post>*******************************************************************



class CommentTreeQueryset(TreeQuerySet):
    def get_available(self):
        queryset = self.filter(status=COMMENT_STATUS_PUBLISHED)
        return queryset


class CommentManager(models.manager.BaseManager.from_queryset(CommentTreeQueryset)):
    use_for_related_fields = True



class Comment(SuperModel, MPTTModel, class_with_published_mixin(COMMENT_STATUS_PUBLISHED)):
    class Meta:
        ordering = ['created']
    post = models.ForeignKey(Post, related_name='comments')
    username = models.CharField(max_length=256, verbose_name='Имя')
    email = models.EmailField(verbose_name='E-Mail')
    post_mark = models.IntegerField(choices=POST_MARKS_FOR_COMMENT, blank=True, null=True, verbose_name='Оценка')
    body = models.TextField(verbose_name='Сообщение')
    user = models.ForeignKey(User, null=True, blank=True, related_name='comments')
    ip = models.CharField(max_length=15)
    session_key = models.TextField(blank=True)
    consult_required = models.BooleanField(default=False, verbose_name='Нужна консультация провизора')
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    status = models.IntegerField(choices=COMMENT_STATUSES, verbose_name='Статус')
    updater = models.ForeignKey(User, null=True, blank=True, related_name='updated_comments')
    key = models.CharField(max_length=128, blank=True)
    confirmed = models.BooleanField(default=False)
    old_id = models.PositiveIntegerField(null=True, blank=True)

    objects = CommentManager()

    def __str__(self):
        return self.short_body


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

    def get_children_tree(self, cur=None, level=1):
        tree = []
        if cur is None:
            cur = self
        else:
            tree.append(cur)
        for child in cur.children.get_available().order_by('created'):
            child.tree_level = level
            tree += child.get_children_tree(child, level+1)
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

    def send_confirmation_mail(self, user=None, request=None):
        if not user and request:
            user = request.user
        if request:
            ip = get_client_ip(request)
            session_key = request.session.session_key
        else:
            ip = None
            session_key = None

        confirm_comment_text_template_name = 'prozdo_main/mail/confirm_comment_html_template.html'
        confirm_comment_html_template_name = 'prozdo_main/mail/confirm_comment_text_template.txt'
        if not user.email_confirmed and not self.confirmed:
                html = render_to_string(confirm_comment_html_template_name, {'comment': self})
                text = render_to_string(confirm_comment_text_template_name, {'comment': self})
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
                        )
                except:
                    pass



    @property
    def available_children(self):
        return self.get_descendants().filter(status=COMMENT_STATUS_PUBLISHED)


    @property
    def short_body(self):
        return cut_text(self.body)


    @property
    def comment_mark(self):
        try:
            mark = History.objects.filter(comment=self, history_type=HISTORY_TYPE_COMMENT_RATED).aggregate(Count('pk'))['pk__count']
            if mark is None:
                mark = 0
        except:
            mark = 0
        return mark


    def get_absolute_url(self):
        if self.status == COMMENT_STATUS_PUBLISHED:
            return '{0}/comment/{1}#c{1}'.format(self.post.get_absolute_url(), self.pk)
        else:
            return self.post.get_absolute_url()

    def get_confirm_url(self):
        return settings.SITE_URL + reverse('comment-confirm', kwargs={'comment_pk': self.pk, 'key': self.key})


    def get_status(self):
        if self.user and (self.user.is_admin or self.user.is_author or self.user.is_doctor):
            return COMMENT_STATUS_PUBLISHED
        else:
            if comment_body_ok(self.body) and comment_author_ok(self.username):
                return COMMENT_STATUS_PUBLISHED
            else:
                return COMMENT_STATUS_PENDING_APPROVAL

    @property
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
            return generate_key(128)

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



    def performed_action(self, history_type, user=None, ip=None, request=None):
        if not ip and request:
            ip = get_client_ip(request)
        if not user and request:
            user = request.user

        if user and user.is_authenticated():
            hist_exists = History.objects.filter(history_type=history_type, comment=self, user=user).exists()
        else:
            hist_exists_by_ip = History.objects.filter(history_type=history_type, comment=self, ip=ip).exists()
            hist_exists_by_key = History.objects.filter(history_type=history_type, comment=self).exists()
            hist_exists = hist_exists_by_ip or hist_exists_by_key

        return hist_exists

    def can_perform_action(self, history_type, user=None, ip=None, request=None):
        return not self.performed_action(history_type=history_type, user=user, ip=ip, request=request) and not self.is_author(user=user, ip=ip, request=request)

    def can_undo_action(self, history_type, user):
        if user.is_authenticated():
            res = self.performed_action(history_type=history_type, user=user)
        else:
            res = False
        return res


    def is_author(self, user=None, ip=None, request=None):
        if not ip and request:
            ip = get_client_ip(request)
        if not user and request:
            user = request.user
        if user and user.is_authenticated():
            res = self.user == user
        else:
            res = self.ip == ip
        return res



HISTORY_TYPE_COMMENT_CREATED = 1
HISTORY_TYPE_COMMENT_SAVED = 2
HISTORY_TYPE_COMMENT_RATED = 3
HISTORY_TYPE_POST_CREATED = 4
HISTORY_TYPE_POST_SAVED = 5
HISTORY_TYPE_POST_RATED = 6
HISTORY_TYPE_COMMENT_COMPLAINT = 7
HISTORY_TYPE_POST_COMPLAINT = 8

HISTORY_TYPES = (
    (HISTORY_TYPE_COMMENT_CREATED, 'Комментарий создан'),
    (HISTORY_TYPE_COMMENT_SAVED, 'Комментарий сохранен'),
    (HISTORY_TYPE_COMMENT_RATED, 'Комментарий оценен'),
    (HISTORY_TYPE_POST_CREATED, 'Пост создан'),
    (HISTORY_TYPE_POST_SAVED, 'Пост сохранен'),
    (HISTORY_TYPE_POST_RATED, 'Пост оценен'),
    (HISTORY_TYPE_COMMENT_COMPLAINT, 'Жалоба на коммент'),
    (HISTORY_TYPE_POST_COMPLAINT, 'Жалоба на пост'),
)

HISTORY_TYPES_POINTS = {
HISTORY_TYPE_COMMENT_CREATED: 3,
HISTORY_TYPE_COMMENT_SAVED: 0,
HISTORY_TYPE_COMMENT_RATED: 1,
HISTORY_TYPE_POST_CREATED: 0,
HISTORY_TYPE_POST_SAVED: 0,
HISTORY_TYPE_POST_RATED: 1,
HISTORY_TYPE_COMMENT_COMPLAINT: 0,
HISTORY_TYPE_POST_COMPLAINT: 0,
}


class History(SuperModel):
    post = models.ForeignKey(Post, related_name='history_post')
    history_type = models.IntegerField(choices=HISTORY_TYPES)
    author = models.ForeignKey(User, null=True, blank=True, related_name='history_author')
    user = models.ForeignKey(User, null=True, blank=True, related_name='history_user')
    comment = models.ForeignKey(Comment, null=True, blank=True, related_name='history_comment')
    user_points = models.PositiveIntegerField(default=0, blank=True)
    #author_points = models.PositiveIntegerField(default=0, blank=True)
    ip = models.CharField(max_length=15, null=True, blank=True)
    session_key = models.TextField(blank=True)
    mark = models.IntegerField(choices=POST_MARKS_FOR_COMMENT, blank=True, null=True, verbose_name='Оценка')
    old_id = models.PositiveIntegerField(null=True, blank=True)

    @staticmethod
    def get_points(history_type):
        return HISTORY_TYPES_POINTS[history_type]

    def __str__(self):
        return "{0} - {1} - {2}".format(self.history_type, self.post, self.comment)


    @staticmethod
    def save_history(history_type, post, user=None, ip=None, session_key=None, comment=None, mark=None):
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
                                       user_points=History.get_points(history_type), ip=ip, author=post_author)
            else:
                h = History.save_history(HISTORY_TYPE_POST_SAVED, post, user, ip, session_key, comment)
            return h
        elif history_type == HISTORY_TYPE_POST_SAVED:
            h = History.objects.create(history_type=history_type, post=post, user=user, ip=ip, author=post_author)
            return h
        elif history_type == HISTORY_TYPE_COMMENT_CREATED:
            hist_exists = History.objects.filter(history_type=history_type, comment=comment).exists()
            if not hist_exists:

                h = History.objects.create(history_type=history_type, post=post, user=user, comment=comment, ip=ip,
                                       user_points=History.get_points(history_type),
                                       author=post_author, mark=mark)
            else:
                h = History.save_history(HISTORY_TYPE_COMMENT_SAVED, post, user, ip, session_key, comment, mark=mark)
            return h
        elif history_type == HISTORY_TYPE_COMMENT_SAVED:
            h = History.objects.create(history_type=history_type, post=post, user=user, comment=comment, ip=ip,
                                   user_points=History.get_points(history_type), author=post_author)
            return h
        elif history_type in [HISTORY_TYPE_COMMENT_RATED, HISTORY_TYPE_COMMENT_COMPLAINT]:
            #if history_type == HISTORY_TYPE_COMMENT_RATED:
            #    author_points = 1
            #else:
            #    author_points = 0

            if comment.can_perform_action(history_type=history_type, user=user, ip=ip):
                h = History.objects.create(history_type=history_type, post=post, user=user, comment=comment, ip=ip,
                                       user_points=History.get_points(history_type),
                                       author=comment.user)
                return h
        elif history_type == HISTORY_TYPE_POST_RATED:
            if user and user.is_authenticated():
                hist_exists = History.objects.filter(history_type=history_type, post=post, user=user).exists()
            else:
                hist_exists = History.objects.filter(history_type=history_type, post=post, ip=ip, user=user).exists()

            if not hist_exists and mark and mark > 0:
                h = History.objects.create(history_type=history_type, post=post, user=user, ip=ip, comment=comment,
                                   user_points=History.get_points(history_type), author=post_author, mark=mark)
                return h
        #При сохранении отзыва сохраняем оценку поста
        #if history_type in [HISTORY_TYPE_COMMENT_CREATED, HISTORY_TYPE_COMMENT_SAVED] and mark:
            #h = History.save_history(HISTORY_TYPE_POST_RATED, post, user=user, ip=ip, comment=comment, mark=mark)
            #return h

class UserProfile(SuperModel):
    # required by the auth model
    user = models.OneToOneField(User, related_name='user_profile')  # reverse returns single object, not queryset
    role = models.PositiveIntegerField(choices=USER_ROLES, default=USER_ROLE_REGULAR, blank=True)
    image = ImageField(verbose_name='Изображение', upload_to='user_profile', blank=True, null=True)
    receive_messages = models.BooleanField(default=True, verbose_name='Получать e-mail сообщения с сайта', blank=True)
    first_name = models.CharField(max_length=800, verbose_name='Имя', blank=True)
    last_name = models.CharField(max_length=800, verbose_name='Фамилия', blank=True)
    old_id = models.PositiveIntegerField(null=True, blank=True)

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


def karm_history(self):
    return self._karm_history.order_by('-created')

def _karm_history(self):
    hists = History.objects.filter(author=self, history_type=HISTORY_TYPE_COMMENT_RATED)
    return hists


def _activity_history(self):
    return History.objects.filter(user=self, user_points__gt=0)

def activity_history(self):
    return self._activity_history.order_by('-created')

def get_user_activity(self):
    try:
        activity =  self._activity_history.aggregate(Sum('user_points'))['user_points__sum']
    except:
        activity = ''
    return activity

def get_email_confirmed(self):
    return EmailAddress.objects.filter(user=self, verified=True, email=self.email).exists()


User.is_regular = property(is_regular)
User.image = property(get_user_image)
User.karm_history = property(karm_history)
User._karm_history = property(_karm_history)
User.activity_history = property(activity_history)
User._activity_history = property(_activity_history)
User.karm = property(lambda self: self._karm_history.count())
User.get_karm_url = lambda self: reverse('user-karma', kwargs={'pk': self.pk})
User.get_comments_url = lambda self: reverse('user-comments', kwargs={'pk': self.pk})
User.get_activity_url = lambda self: reverse('user-activity', kwargs={'pk': self.pk})
User.get_absolute_url = lambda self: reverse('user-detail', kwargs={'pk': self.pk})

User.activity = property(get_user_activity)
User.email_confirmed = property(get_email_confirmed)

User.is_admin = property(lambda self: self.user_profile.role == USER_ROLE_ADMIN)
User.is_author = property(lambda self: self.user_profile.role == USER_ROLE_AUTHOR)
User.is_regular = property(lambda self: self.user_profile.role == USER_ROLE_REGULAR)
User.is_doctor = property(lambda self: self.user_profile.role == USER_ROLE_DOCTOR)
User.thumb100 = property(lambda self: self.user_profile.thumb100)
User.thumb50 = property(lambda self: self.user_profile.thumb50)


AnonymousUser.is_regular = True
AnonymousUser.image = None
AnonymousUser.email_confirmed = False


MAIL_TYPE_COMMENT_CONFIRM = 1
MAIL_TYPE_USER_REGISTRATION = 2
MAIL_TYPE_PASSWORD_RESET = 3

MAIL_TYPES = (
    (MAIL_TYPE_COMMENT_CONFIRM, 'Подтверждение отзыва'),
    (MAIL_TYPE_USER_REGISTRATION, 'Регистрация пользователя'),
    (MAIL_TYPE_COMMENT_CONFIRM, 'Сброс пароля'),
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
