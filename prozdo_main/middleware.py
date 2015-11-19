from django.middleware.cache import UpdateCacheMiddleware, FetchFromCacheMiddleware
from django.conf import settings
from . import models



class ProzdoUpdateCacheMiddleware(UpdateCacheMiddleware):
    def _should_update_cache(self, request, response):
        if not settings.PROZDO_CACHE_ENABLED:
            return False
        if models.request_with_empty_guest(request):
            return super()._should_update_cache(request, response)
        else:
            return False



class ProzdoFetchFromCacheMiddleware(FetchFromCacheMiddleware):
    def process_request(self, request):
        if not settings.PROZDO_CACHE_ENABLED:
            request._cache_update_cache = False
            return None
        if models.request_with_empty_guest(request):
            return super().process_request(request)
        else:
            request._cache_update_cache = False
            return None


class SetClientIpMiddleware:
    def process_request(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        request.client_ip = ip


class SetProzdoKeyMiddleware:
    def process_request(self, request):
        prozdo_key = request.session.get('prozdo_key', None)
        request.session.prozdo_key = prozdo_key