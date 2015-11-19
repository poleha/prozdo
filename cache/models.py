from . import constants
from django.conf import settings
from django.core.cache import cache
from django.db.models import Model
from .decorators import CachedProperty

class CachedModelMixin(Model):
    class Meta:
        abstract = True

    cached_views = tuple()

    def get_cached_property_cache_key(self, attr_name):
        return constants.CACHED_PROPERTY_KEY_TEMPLATE.format(type(self).__name__, attr_name, self.pk)

    def invalidate_cached_property(self, attr_name, delete=True):
        if settings.PROZDO_CACHE_ENABLED:
            key = self.get_cached_property_cache_key(attr_name)
            if delete:
                cache.delete(key)
            res = getattr(self, attr_name)
            if res is None:
                res = constants.EMPTY_CACHE_PLACEHOLDER
            cache.set(key, res, settings.PROZDO_CACHED_PROPERTY_DURATION)

    def full_invalidate_cache(self):
        if settings.PROZDO_CACHE_ENABLED:
            prop_keys = []
            meth_keys = []
            for c in type(self).mro():
                for k, v in c.__dict__.items():
                    if isinstance(v, CachedProperty):
                        prop_keys.append(k)
                    elif hasattr(v, '__is_cached_method__'):
                        meth_keys.append(k)

                #prop_keys += [k for k, v in c.__dict__.items() if isinstance(v, CachedProperty) or v.__name__ == 'wrapper']

            for attr_name in set(prop_keys):
                self.clean_cached_property(attr_name)

            for attr_name in set(prop_keys):
                self.invalidate_cached_property(attr_name, delete=False)

            for attr_name in set(meth_keys):
                cache.delete_pattern(constants.CACHED_METHOD_KEY_TEMPLATE.format(type(self).__name__, attr_name, self.pk) + '*')

            for cls_name, func_name in self.cached_views:
                cache.delete_pattern(constants.CACHED_VIEW_PARTIAL_TEMPLATE_PREFIX.format(cls_name, func_name) + '*')

    def clean_cached_property(self, attr_name):
        if settings.PROZDO_CACHE_ENABLED:
            key = self.get_cached_property_cache_key(attr_name)
            cache.delete(key)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if settings.PROZDO_CACHE_ENABLED:
            self.full_invalidate_cache()