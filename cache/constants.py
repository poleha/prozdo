from django.core.handlers.wsgi import WSGIRequest

EMPTY_CACHE_PLACEHOLDER = '__EMPTY__'
CACHED_VIEW_PARTIAL_TEMPLATE_PREFIX = "_cached_view-{0}-{1}"
CACHED_VIEW_TEMLPATE_PREFIX = CACHED_VIEW_PARTIAL_TEMPLATE_PREFIX + "-{2}"

CACHED_PROPERTY_KEY_TEMPLATE = '_cached_{0}-{1}-{2}'

CACHED_METHOD_KEY_TEMPLATE = '_cached_method_{0}_{1}_{2}'
CACHED_METHOD_KEY_FULL_TEMPLATE = CACHED_METHOD_KEY_TEMPLATE + '_{3}'

CONDITIONAL_CACHE_KEY = '__conditional_cache__{0}'

#TODO change to path.to.WSGIRequest
CACHED_METHOD_SPECIAL_CASES = {
   WSGIRequest: ('user.pk', 'session.prozdo_key', 'client_ip')
}
