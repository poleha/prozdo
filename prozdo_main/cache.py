from django.conf import settings
from django.db.models import Model
from django.core.cache import cache
from .helper import get_class_that_defined_method
#from .models import History

EMPTY_CACHE_PLACEHOLDER = '__EMPTY__'
CACHED_VIEW_PARTIAL_TEMPLATE_PREFIX = "_cached_view-{0}-{1}"
CACHED_VIEW_TEMLPATE_PREFIX = CACHED_VIEW_PARTIAL_TEMPLATE_PREFIX + "-{2}"

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
                cache.set(key, res, settings.PROZDO_CACHED_PROPERTY_DURATION)
            if res == EMPTY_CACHE_PLACEHOLDER:
                res = None
            return res
        else:
            return func(self)
    return wrapper

CACHED_METHOD_SHORT_KEY_TEMPLATE = '_cached_method_{0}_{1}'
CACHED_METHOD_KEY_TEMPLATE = CACHED_METHOD_SHORT_KEY_TEMPLATE + '_{2}_{3}'


class CachedModelMixin(Model):
    class Meta:
        abstract = True

    cache_key_template = CACHED_ATTRIBUTE_KEY_TEMPLATE

    cached_views = tuple()

    def get_cache_key(self, attr_name):
        return self.cache_key_template.format(type(self).__name__, attr_name, self.pk)

    def invalidate_cache(self, attr_name):
        if settings.PROZDO_CACHE_ENABLED:
            key = self.get_cache_key(attr_name)
            cache.delete(key)
            res = getattr(self, attr_name)
            if res is None:
                res = EMPTY_CACHE_PLACEHOLDER
            cache.set(key, res, settings.PROZDO_CACHED_PROPERTY_DURATION)

    def full_invalidate_cache(self):
        if settings.PROZDO_CACHE_ENABLED:
            prop_keys = []
            for c in type(self).mro():
                prop_keys += [k for k, v in c.__dict__.items() if isinstance(v, CachedProperty)]

            for attr_name in set(prop_keys):
                self.invalidate_cache(attr_name)

            for cls_name, func_name in self.cached_views:
                cache.delete_pattern(CACHED_VIEW_PARTIAL_TEMPLATE_PREFIX.format(cls_name, func_name) + '*')

    def clean_cache(self, attr_name):
        if settings.PROZDO_CACHE_ENABLED:
            key = self.get_cache_key(attr_name)
            cache.delete(key)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if settings.PROZDO_CACHE_ENABLED:
            self.full_invalidate_cache()


def cached_view(timeout=settings.PROZDO_CACHE_DURATION, test=lambda request: True):
    def decorator(func):
        def wrapper(self, request, *args, **kwargs):
            if settings.PROZDO_CACHE_ENABLED and test(request):
                url = request.build_absolute_uri()
                cls = get_class_that_defined_method(func)
                flavour = getattr(request, 'flavour', '')
                prefix = CACHED_VIEW_TEMLPATE_PREFIX.format(cls.__name__, func.__name__, flavour)
                key = "{0}-{1}".format(prefix, url)
                res = cache.get(key)
                if res is None:
                    res = func(self, request, *args, **kwargs)
                    res.render()
                    cache.set(key, res, timeout)
            else:
                res = func(self, request, *args, **kwargs)
            return res
        return wrapper
    return decorator


