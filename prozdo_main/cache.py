from django.conf import settings
from django.db.models import Model
from django.core.cache import cache
from .helper import get_class_that_defined_method
#from .models import History

EMPTY_CACHE_PLACEHOLDER = '__EMPTY__'
CACHED_VIEW_PARTIAL_TEMPLATE_PREFIX = "_cached_view-{0}-{1}"
CACHED_VIEW_TEMLPATE_PREFIX = CACHED_VIEW_PARTIAL_TEMPLATE_PREFIX + "-{2}"

CACHED_PROPERTY_KEY_TEMPLATE = '_cached_{0}-{1}-{2}'


from django.core.handlers.wsgi import WSGIRequest


CACHED_METHOD_SPECIAL_CASES = {
   WSGIRequest: ('user.pk', 'session.prozdo_key', 'client_ip')
}


class CachedProperty(property):
    pass

def cached_property(func):
    @CachedProperty
    def wrapper(self):
        if settings.CACHE_ENABLED:
            key = CACHED_PROPERTY_KEY_TEMPLATE.format(type(self).__name__, func.__name__, self.pk)
            res = cache.get(key)
            if res is None:
                res = func(self)
                if res is None:
                    res = EMPTY_CACHE_PLACEHOLDER
                cache.set(key, res, settings.CACHED_PROPERTY_DURATION)
            if res == EMPTY_CACHE_PLACEHOLDER:
                res = None
            return res
        else:
            return func(self)
    return wrapper

from django.db.models import Model
CACHED_METHOD_KEY_TEMPLATE = '_cached_method_{0}_{1}_{2}'
CACHED_METHOD_KEY_FULL_TEMPLATE = CACHED_METHOD_KEY_TEMPLATE + '_{3}'

def rec_getattr(obj, attr):
    try:
        if '.' not in attr:
            try:
                return getattr(obj, attr)
            except:
                return obj.get(attr, None)
        else:
            L = attr.split('.')
            return rec_getattr(getattr(obj, L[0]), '.'.join(L[1:]))
    except:
        return None

def make_key_from_args(args, kwargs):
    res_args = ''
    for arg in args + tuple(kwargs.values()):
        if isinstance(arg, tuple(CACHED_METHOD_SPECIAL_CASES.keys())):
            res_arg = type(arg).__name__
            for v in CACHED_METHOD_SPECIAL_CASES[type(arg)]:
                res_arg += '_' + str(rec_getattr(arg, v))
            res_args += '_' + res_arg
        elif isinstance(arg, Model):
            res_args += '{0}-{1}'.format(type(arg).__name__, arg.pk)
        elif isinstance(arg, str):
            res_args += '_' + arg
        else:
            res_args += '_' + str(arg)
    return res_args

def cached_method(timeout=settings.CACHED_METHOD_DURATION):
    def _cached_method(func):
        def wrapper(self, *args, **kwargs):
            if settings.CACHE_ENABLED:
                key = CACHED_METHOD_KEY_FULL_TEMPLATE.format(type(self).__name__, func.__name__, self.pk, make_key_from_args(args, kwargs))
                res = cache.get(key)
                if res is None:
                    res = func.__get__(self)(*args, **kwargs)
                    if res is None:
                        res = EMPTY_CACHE_PLACEHOLDER
                    cache.set(key, res, timeout)
                if res == EMPTY_CACHE_PLACEHOLDER:
                    res = None
                return res
            else:
                return func.__get__(self)(*args, **kwargs)
        wrapper.__is_cached_method__ = True
        return wrapper
    return _cached_method



class CachedModelMixin(Model):
    class Meta:
        abstract = True

    cached_views = tuple()

    def get_cached_property_cache_key(self, attr_name):
        return CACHED_PROPERTY_KEY_TEMPLATE.format(type(self).__name__, attr_name, self.pk)

    def invalidate_cached_property(self, attr_name, delete=True):
        if settings.CACHE_ENABLED:
            key = self.get_cached_property_cache_key(attr_name)
            if delete:
                cache.delete(key)
            res = getattr(self, attr_name)
            if res is None:
                res = EMPTY_CACHE_PLACEHOLDER
            cache.set(key, res, settings.CACHED_PROPERTY_DURATION)

    def full_invalidate_cache(self):
        if settings.CACHE_ENABLED:
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
                cache.delete_pattern(CACHED_METHOD_KEY_TEMPLATE.format(type(self).__name__, attr_name, self.pk) + '*')

            for cls_name, func_name in self.cached_views:
                cache.delete_pattern(CACHED_VIEW_PARTIAL_TEMPLATE_PREFIX.format(cls_name, func_name) + '*')

    def clean_cached_property(self, attr_name):
        if settings.CACHE_ENABLED:
            key = self.get_cached_property_cache_key(attr_name)
            cache.delete(key)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if settings.CACHE_ENABLED:
            self.full_invalidate_cache()


def cached_view(timeout=settings.CACHED_VIEW_DURATION, test=lambda request: True):
    def decorator(func):
        def wrapper(self, request, *args, **kwargs):
            if settings.CACHE_ENABLED and test(request):
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

CONDITIONAL_CACHE_KEY = '__conditional_cache__{0}'

def set_conditional_cache(key, value, condition, expires=None):
    condition_key = CONDITIONAL_CACHE_KEY.format(key)
    cache.set(condition_key, condition, expires)
    cache.set(key, value, expires)


def get_conditional_cache(key, condition):
    condition_key = CONDITIONAL_CACHE_KEY.format(key)
    stored_condition = cache.get(condition_key)
    if not stored_condition == condition:
        cache.delete_many([key, condition_key])
    return cache.get(key)
