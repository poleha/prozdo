import os, re
from sorl.thumbnail.base import ThumbnailBackend
from django.template.defaultfilters import slugify
from django.conf import settings

class SEOThumbnailBackend(ThumbnailBackend):
    """
    Custom backend for SEO-friendly thumbnail file names/urls.
    """
    def _get_thumbnail_filename(self, source, geometry_string, options):
        """
        Computes the destination filename.
        """

        split_path = re.sub(r'^%s%s?' % (source.storage.path(''), os.sep), '', source.name).split(os.sep)
        split_path.insert(-1, geometry_string)

        #attempt to slugify the filename to make it SEO-friendly
        split_name = split_path[-1].split('.')
        try:
            split_path[-1] = '%s.%s' % (slugify('.'.join(split_name[:-1])), split_name[-1])
        except:
            #on fail keep the original filename
            pass

        path = os.sep.join(split_path)

        #if the path already starts with THUMBNAIL_PREFIX do not concatenate the PREFIX
        #this way we avoid ending up with a url like /images/images/120x120/my.png
        if not path.startswith(settings.THUMBNAIL_PREFIX):
            return '%s%s' % (settings.THUMBNAIL_PREFIX, path)

        return path



from django.core.cache.backends.db import DatabaseCache


class ProzdoCacheBackendMixin:
    def get(self, key, default=None, version=None):
        if settings.PROZDO_CACHE_ENABLED:
            return super().get(key, default, version)
        else:
            return None

    def set(self, key, value, timeout=None, version=None):
        if settings.PROZDO_CACHE_ENABLED:
            return super().set(key, value, timeout, version)
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