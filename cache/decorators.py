from django.conf import settings
from . import constants
from django.core.cache import cache
from prozdo_main.helper import get_class_that_defined_method
from .helper import make_key_from_args


class CachedProperty(property):
    pass

def cached_property(func):
    @CachedProperty
    def wrapper(self):
        if settings.PROZDO_CACHE_ENABLED:
            key = constants.CACHED_PROPERTY_KEY_TEMPLATE.format(type(self).__name__, func.__name__, self.pk)
            res = cache.get(key)
            if res is None:
                res = func(self)
                if res is None:
                    res = constants.EMPTY_CACHE_PLACEHOLDER
                cache.set(key, res, settings.PROZDO_CACHED_PROPERTY_DURATION)
            if res == constants.EMPTY_CACHE_PLACEHOLDER:
                res = None
            return res
        else:
            return func(self)
    return wrapper

def cached_method(timeout=settings.PROZDO_CACHED_METHOD_DURATION):
    def _cached_method(func):
        def wrapper(self, *args, **kwargs):
            if settings.PROZDO_CACHE_ENABLED:
                key = constants.CACHED_METHOD_KEY_FULL_TEMPLATE.format(type(self).__name__, func.__name__, self.pk, make_key_from_args(args, kwargs))
                res = cache.get(key)
                if res is None:
                    res = func.__get__(self)(*args, **kwargs)
                    if res is None:
                        res = constants.EMPTY_CACHE_PLACEHOLDER
                    cache.set(key, res, timeout)
                if res == constants.EMPTY_CACHE_PLACEHOLDER:
                    res = None
                return res
            else:
                return func.__get__(self)(*args, **kwargs)
        wrapper.__is_cached_method__ = True
        return wrapper
    return _cached_method

def cached_view(timeout=settings.PROZDO_CACHED_VIEW_DURATION, test=lambda request: True):
    def decorator(func):
        def wrapper(self, request, *args, **kwargs):
            if settings.PROZDO_CACHE_ENABLED and test(request):
                url = request.build_absolute_uri()
                cls = get_class_that_defined_method(func)
                flavour = getattr(request, 'flavour', '')
                prefix = constants.CACHED_VIEW_TEMLPATE_PREFIX.format(cls.__name__, func.__name__, flavour)
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