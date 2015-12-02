from django.db import models
from django.utils import timezone
from cache.models import CachedModelMixin
from mptt.models import MPTTModel, TreeForeignKey
from mptt.querysets import TreeQuerySet
from django.contrib.auth.models import User
from cache.decorators import cached_property
from django.conf import settings
from django.core.urlresolvers import reverse
from math import ceil
from helper import helper
from django.utils.html import strip_tags

class SuperModel(models.Model):
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


COMMENT_STATUS_PENDING_APPROVAL = 1
COMMENT_STATUS_PUBLISHED = 2

COMMENT_STATUSES = (
    (COMMENT_STATUS_PENDING_APPROVAL, 'На согласовании'),
    (COMMENT_STATUS_PUBLISHED, 'Опубликован'),
)


class CommentTreeQueryset(TreeQuerySet):
    def get_available(self):
        queryset = self.filter(status=COMMENT_STATUS_PUBLISHED)
        return queryset



class CommentManager(models.manager.BaseManager.from_queryset(CommentTreeQueryset)):
    use_for_related_fields = True


class SuperComment(SuperModel, CachedModelMixin, MPTTModel, class_with_published_mixin(COMMENT_STATUS_PUBLISHED)):
    class Meta:
        abstract = True

    username = models.CharField(max_length=256, verbose_name='Имя')
    email = models.EmailField(verbose_name='E-Mail')
    body = models.TextField(verbose_name='Сообщение')
    user = models.ForeignKey(User, null=True, blank=True, related_name='comments', db_index=True)
    ip = models.CharField(max_length=300, db_index=True)
    session_key = models.TextField(blank=True, null=True, db_index=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    status = models.IntegerField(choices=COMMENT_STATUSES, verbose_name='Статус', db_index=True)
    updater = models.ForeignKey(User, null=True, blank=True, related_name='updated_comments')
    key = models.CharField(max_length=128, blank=True)

    objects = CommentManager()

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

    @cached_property
    def available_children(self):
        return self.get_descendants().filter(status=COMMENT_STATUS_PUBLISHED)

    @cached_property
    def available_children_count(self):
        return self.available_children.count()

    @cached_property
    def available_first_level_children(self):
        return type(self).objects.filter(parent=self)

    @property
    def short_body(self):
        return helper.cut_text(strip_tags(self.body))

    @cached_property
    def _cached_get_absolute_url(self):
        if self.status == COMMENT_STATUS_PUBLISHED:
            #return '{0}comment/{1}#c{1}'.format(self.post.get_absolute_url(), self.pk)
            return reverse('post-detail-pk-comment', kwargs={'pk': self.post.pk, 'comment_pk': self.pk}) + '#c' + str(self.pk)
        else:
            return self.post.get_absolute_url()

    def get_absolute_url(self):
        return self._cached_get_absolute_url

    def save(self, *args, **kwargs):
        if not self.confirmed:
            if self.user and self.user.email_confirmed:
                self.confirmed = True
            elif self.email in settings.AUTO_APPROVE_EMAILS:
                self.confirmed = True

        if not self.key:
            self.key = self.generate_key()

        if not self.user or self.user.is_regular:
            self.body = strip_tags(self.body)
        super().save(*args, **kwargs)


