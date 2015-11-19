from django.core.cache import cache
from . import constants

def set_conditional_cache(key, value, condition, expires=None):
    condition_key = constants.CONDITIONAL_CACHE_KEY.format(key)
    cache.set(condition_key, condition, expires)
    cache.set(key, value, expires)


def get_conditional_cache(key, condition):
    condition_key = constants.CONDITIONAL_CACHE_KEY.format(key)
    stored_condition = cache.get(condition_key)
    if not stored_condition == condition:
        cache.delete_many([key, condition_key])
    return cache.get(key)
