from django.middleware.cache import UpdateCacheMiddleware, FetchFromCacheMiddleware
from django.conf import settings
from . import models



class ProzdoUpdateCacheMiddleware(UpdateCacheMiddleware):
    def _should_update_cache(self, request, response):
        if not settings.CACHE_ENABLED:
            return False
        if models.request_with_empty_guest(request):
            return super()._should_update_cache(request, response)
        else:
            return False



class ProzdoFetchFromCacheMiddleware(FetchFromCacheMiddleware):
    def process_request(self, request):
        if not settings.CACHE_ENABLED:
            request._cache_update_cache = False
            return None
        if models.request_with_empty_guest(request):
            return super().process_request(request)
        else:
            request._cache_update_cache = False
            return None


