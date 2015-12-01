from django.db import models
from django.utils import timezone


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
