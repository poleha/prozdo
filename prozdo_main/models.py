from django.db import models
from django.contrib.auth.models import User
from helper import helper
from django.db.models.aggregates import Sum, Count
from django.conf import settings
from django.core.urlresolvers import reverse
from mptt.models import MPTTModel, TreeForeignKey, TreeManager
from mptt.fields import TreeManyToManyField
from allauth.account.models import EmailAddress, EmailConfirmation
from sorl.thumbnail import ImageField, get_thumbnail
from django.utils.html import strip_tags
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from cache.models import CachedModelMixin
from cache.decorators import cached_property, cached_method
from super_model import models as super_models


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


class History(super_models.SuperHistory):
    post = models.ForeignKey('Post', related_name='history_post', db_index=True)


class Post(super_models.SuperPost):
    old_id = models.PositiveIntegerField(null=True, blank=True)

    history_class = History

    cached_views = (
        ('prozdo_main.views.PostDetail', 'get'),
    )

    @classmethod
    def get_post_type(cls):
        if cls == Drug:
            return settings.POST_TYPE_DRUG
        elif cls == Blog:
            return settings.POST_TYPE_BLOG
        elif cls == Component:
            return settings.POST_TYPE_COMPONENT
        elif cls == Cosmetics:
            return settings.POST_TYPE_COSMETICS
        elif cls == Brand:
            return settings.POST_TYPE_BRAND
        elif cls == DrugDosageForm:
            return settings.POST_TYPE_DRUG_DOSAGE_FORM
        elif cls == CosmeticsDosageForm:
            return settings.POST_TYPE_COSMETICS_DOSAGE_FORM
        elif cls == CosmeticsLine:
            return settings.POST_TYPE_COSMETICS_LINE
        elif cls == CosmeticsUsageArea:
            return settings.POST_TYPE_COSMETICS_USAGE_AREA
        elif cls == DrugUsageArea:
            return settings.POST_TYPE_DRUG_USAGE_AREA
        elif cls == Category:
            return settings.POST_TYPE_CATEGORY

    @property
    def is_drug(self):
        return self.post_type == settings.POST_TYPE_DRUG

    @property
    def is_blog(self):
        return self.post_type == settings.POST_TYPE_BLOG

    @property
    def is_component(self):
        return self.post_type == settings.POST_TYPE_COMPONENT

    @property
    def is_cosmetics(self):
        return self.post_type == settings.POST_TYPE_COSMETICS


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
        if self.post_type == settings.POST_TYPE_DRUG:
            return self.drug
        elif self.post_type == settings.POST_TYPE_COMPONENT:
            return self.component
        elif self.post_type == settings.POST_TYPE_BLOG:
            return self.blog
        elif self.post_type == settings.POST_TYPE_COSMETICS:
            return self.cosmetics
        elif self.post_type == settings.POST_TYPE_BRAND:
            return self.brand
        elif self.post_type == settings.POST_TYPE_DRUG_DOSAGE_FORM:
            return self.drugdosageform
        elif self.post_type == settings.POST_TYPE_COSMETICS_DOSAGE_FORM:
            return self.cosmeticsdosageform
        elif self.post_type == settings.POST_TYPE_COSMETICS_LINE:
            return self.cosmeticsline
        elif self.post_type == settings.POST_TYPE_COSMETICS_USAGE_AREA:
            return self.cosmeticsusagearea
        elif self.post_type == settings.POST_TYPE_DRUG_USAGE_AREA:
            return self.drugusagearea
        elif self.post_type == settings.POST_TYPE_CATEGORY:
            return self.category

    def get_absolute_url(self):
        alias = self.alias
        if alias:
            return reverse('post-detail-alias', kwargs={'alias': alias})
        else:
            return reverse('post-detail-pk', kwargs={'pk': self.pk})

    def get_mark_by_request(self, request):
        if super_models.request_with_empty_guest(request):
            return 0
        user = request.user
        if user.is_authenticated():
            try:
                mark = History.objects.get(user=user, history_type=super_models.HISTORY_TYPE_POST_RATED, post=self, deleted=False).mark
            except:
                mark = ''
        else:
            try:
                mark = History.objects.get(post=self, session_key=getattr(request.session, settings.SUPER_MODEL_KEY_NAME), history_type=super_models.HISTORY_TYPE_POST_RATED, user=None, deleted=False).mark
            except:
                mark = 0

        return mark

    @cached_property
    def average_mark(self):
        try:
            mark = History.objects.filter(post=self, deleted=False).aggregate(Sum('mark'))['mark__sum']
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
        return History.objects.filter(post=self, history_type=super_models.HISTORY_TYPE_POST_RATED, deleted=False).count()


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
    component_type = models.IntegerField(choices=COMPONENT_TYPES, verbose_name='Тип компонента', db_index=True)
    objects = super_models.PostManager()

    def type_str(self):
        return 'Компонент'

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
    image = ImageField(verbose_name='Изображение', upload_to='drug', blank=True, null=True, max_length=300)

    dosage_forms = models.ManyToManyField(DrugDosageForm, verbose_name='Формы выпуска')
    usage_areas = models.ManyToManyField(DrugUsageArea, verbose_name='Область применения')
    components = models.ManyToManyField(Component, verbose_name='Состав', blank=True, related_name='drugs')
    category = TreeManyToManyField(Category, verbose_name='Категория', blank=True, db_index=True)
    objects = super_models.PostManager()

    def type_str(self):
        return 'Препарат'

    @property
    def thumb110(self):
        try:
            return get_thumbnail(self.image, '110x200', quality=settings.DEFAULT_THUMBNAIL_QUALITY).url
        except:
            return ''

    @property
    def thumb150(self):
        try:
            return get_thumbnail(self.image, '150x300', quality=settings.DEFAULT_THUMBNAIL_QUALITY).url
        except:
            return ''

    @property
    def thumb220(self):
        try:
            return get_thumbnail(self.image, '220x400', quality=settings.DEFAULT_THUMBNAIL_QUALITY).url
        except:
            return ''

class Cosmetics(Post):
    body = RichTextField(verbose_name='Содержимое', blank=True)
    image = ImageField(verbose_name='Изображение', upload_to='cosmetics', blank=True, null=True, max_length=300)

    brand = models.ForeignKey(Brand, verbose_name='Бренд', db_index=True)
    line = models.ForeignKey(CosmeticsLine, verbose_name='Линейка', null=True, blank=True, db_index=True)
    dosage_forms = models.ManyToManyField(CosmeticsDosageForm, verbose_name='Формы выпуска')
    usage_areas = models.ManyToManyField(CosmeticsUsageArea, verbose_name='Область применения')
    objects = super_models.PostManager()

    def type_str(self):
        return 'Косметика'

    #TODO проверить, убрать лишнее
    @property
    def thumb110(self):
        try:
            return get_thumbnail(self.image, '110x200', quality=settings.DEFAULT_THUMBNAIL_QUALITY).url
        except:
            return ''

    @property
    def thumb150(self):
        try:
            return get_thumbnail(self.image, '150x300', quality=settings.DEFAULT_THUMBNAIL_QUALITY).url
        except:
            return ''

    @property
    def thumb220(self):
        try:
            return get_thumbnail(self.image, '220x400', quality=settings.DEFAULT_THUMBNAIL_QUALITY).url
        except:
            return ''

class Blog(Post):
    class Meta:
        ordering = ('-created', )
    short_body = models.TextField(verbose_name='Анонс', blank=True)
    body = RichTextUploadingField(verbose_name='Содержимое', blank=True)
    image = ImageField(verbose_name='Изображение', upload_to='blog', blank=True, null=True, max_length=300)
    category = TreeManyToManyField(Category, verbose_name='Категория', db_index=True)
    objects = super_models.PostManager()

    def type_str(self):
        return 'Запись блога'

    @property
    def thumb110(self):
        try:
            return get_thumbnail(self.image, '110x200', quality=settings.DEFAULT_THUMBNAIL_QUALITY).url
        except:
            return ''

    @property
    def thumb150(self):
        try:
            return get_thumbnail(self.image, '150x300', quality=settings.DEFAULT_THUMBNAIL_QUALITY).url
        except:
            return ''

    @property
    def thumb220(self):
        try:
            return get_thumbnail(self.image, '220x400', quality=settings.DEFAULT_THUMBNAIL_QUALITY).url
        except:
            return ''

    @property
    def thumb360(self):
        try:
            return get_thumbnail(self.image, '360x720', quality=settings.DEFAULT_THUMBNAIL_QUALITY).url
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
            mark = History.objects.filter(post=self, history_type=super_models.HISTORY_TYPE_POST_RATED, deleted=False).aggregate(Count('pk'))['pk__count']
            if mark is None:
                mark = 0
        except:
            mark = 0
        return mark

    def get_mark_blog_by_request(self, request):
        user = request.user
        if user.is_authenticated():
            try:
                mark = History.objects.filter(user=user, history_type=super_models.HISTORY_TYPE_POST_RATED, post=self, deleted=False).count()
            except:
                mark = 0
        else:
            try:
                mark = History.objects.filter(post=self, history_type=super_models.HISTORY_TYPE_POST_RATED, user=None, deleted=False).filter(session_key=getattr(request.session, settings.SUPER_MODEL_KEY_NAME)).count()
            except:
                mark = 0

        return mark


class Comment(super_models.SuperComment):
    class Meta:
        ordering = ['-created']
    post = models.ForeignKey(Post, related_name='comments', db_index=True)
    consult_required = models.BooleanField(default=False, verbose_name='Нужна консультация провизора', db_index=True)
    old_id = models.PositiveIntegerField(null=True, blank=True)
    txt_template_name = 'prozdo_main/comment/email/answer_to_comment.txt'
    html_template_name = 'prozdo_main/comment/email/answer_to_comment.html'

    confirm_comment_text_template_name = 'prozdo_main/comment/email/confirm_comment_html_template.html'
    confirm_comment_html_template_name = 'prozdo_main/comment/email/confirm_comment_text_template.txt'

    def __str__(self):
        return self.short_body

    def type_str(self):
        return 'Сообщение'

    def get_confirm_url(self):
        return reverse('comment-confirm', kwargs={'comment_pk': self.pk, 'key': self.key})

    @property
    def consult_done(self):
        return self.available_children.filter(user__user_profile__role=super_models.USER_ROLE_DOCTOR).exists()

    @cached_property
    def comment_mark(self):
        try:
            mark = History.objects.filter(comment=self, history_type=super_models.HISTORY_TYPE_COMMENT_RATED, deleted=False).aggregate(Count('pk'))['pk__count']
            if mark is None:
                mark = 0
        except:
            mark = 0
        return mark

    @cached_property
    def complain_count(self):
        try:
            count = History.objects.filter(comment=self, history_type=super_models.HISTORY_TYPE_COMMENT_COMPLAINT, deleted=False).aggregate(Count('pk'))['pk__count']
            if count is None:
                count = 0
        except:
            count = 0
        return count

    @cached_method()
    def hist_exists_by_comment_and_user(self, history_type, user):
        return History.objects.filter(history_type=history_type, comment=self, user=user, deleted=False).exists()

    def hist_exists_by_request(self, history_type, request):
        if super_models.request_with_empty_guest(request):
            return False
        user = request.user
        if user and user.is_authenticated():
            hist_exists = self.hist_exists_by_comment_and_user(history_type, user)
        else:
            session_key = getattr(request.session, settings.SUPER_MODEL_KEY_NAME, None)
            if session_key is None:
                return False
            hist_exists = History.exists_by_comment(session_key, self, history_type)
        return hist_exists

    def show_do_action_button(self, history_type, request):
        if super_models.request_with_empty_guest(request):
            return True
        return not self.hist_exists_by_request(history_type, request) and not self.is_author_for_show_buttons(request)

    def show_undo_action_button(self, history_type, request):
        if super_models.request_with_empty_guest(request):
            return False
        return self.hist_exists_by_request(history_type, request) and not self.is_author_for_show_buttons(request)

    def is_author_for_show_buttons(self, request):
        if super_models.request_with_empty_guest(request):
            return False
        user = request.user
        if user and user.is_authenticated():
            return user == self.user
        else:
            session_key = getattr(request.session, settings.SUPER_MODEL_KEY_NAME, None)
            if session_key is None:
                return False
            else:
                return self.session_key == session_key


    def hist_exists_by_data(self, history_type, user=None, ip=None, session_key=None):
        if user and user.is_authenticated():
            hist_exists = History.objects.filter(history_type=history_type, comment=self, user=user, deleted=False).exists()
        elif not History.exists(session_key):
            return False
        else:
            if session_key:
                hist_exists_by_key = History.objects.filter(history_type=history_type, comment=self, session_key=session_key, deleted=False).exists()
            else:
                hist_exists_by_key = False
            if ip:
                hist_exists_by_ip = History.objects.filter(history_type=history_type, comment=self, ip=ip, deleted=False).exists()
            else:
                hist_exists_by_ip = False
            hist_exists = hist_exists_by_key or hist_exists_by_ip

        return hist_exists

    def can_do_action(self, history_type, user, ip, session_key):
        if user and not user.is_authenticated():
            return True
        return not self.hist_exists_by_data(history_type, user, ip, session_key) and not self.is_author_for_save_history(user, ip, session_key)


class UserProfile(super_models.SuperUserProfile):
    old_id = models.PositiveIntegerField(null=True, blank=True)

    @cached_property
    def can_publish_comment(self):
        if self.user.is_admin or self.user.is_author or self.user.is_doctor or self.get_user_karm >= settings.PUBLISH_COMMENT_WITHOUT_APPROVE_KARM:
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
        hists = History.objects.filter(author=self.user, history_type=super_models.HISTORY_TYPE_COMMENT_RATED, deleted=False)
        return hists


    def _activity_history(self):
        return History.objects.filter(user=self.user, user_points__gt=0, deleted=False)

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

    @property
    def thumb50(self):
        try:
            return get_thumbnail(self.image, '50x50', quality=settings.DEFAULT_THUMBNAIL_QUALITY).url
        except:
            return ''

    @property
    def thumb100(self):
        try:
            return get_thumbnail(self.image, '100x100', quality=settings.DEFAULT_THUMBNAIL_QUALITY).url
        except:
            return ''

class Mail(super_models.SuperMail):
    pass


User.is_author = property(lambda self: self.user_profile.role == settings.USER_ROLE_AUTHOR)
User.is_doctor = property(lambda self: self.user_profile.role == settings.USER_ROLE_DOCTOR)