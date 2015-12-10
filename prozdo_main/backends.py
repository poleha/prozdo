from django.conf import settings
from django.core.cache.backends.db import DatabaseCache


class ProzdoCacheBackendMixin:
    def get(self, *args, **kwargs):
        if settings.CACHE_ENABLED:
            return super().get(*args, **kwargs)
        else:
            return None

    def set(self, *args, **kwargs):
        if settings.CACHE_ENABLED:
            return super().set(*args, **kwargs)
        else:
            return None



class ProzdoDBCacheBackend(ProzdoCacheBackendMixin, DatabaseCache):
    pass

from django.core.cache.backends.memcached import MemcachedCache
class ProzdoMemcachedCacheCacheBackend(ProzdoCacheBackendMixin, MemcachedCache):
    pass

from redis_cache.cache import RedisCache
class ProzdoRedisCacheBackend(ProzdoCacheBackendMixin, RedisCache):
    pass