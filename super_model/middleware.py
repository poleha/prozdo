from helper.helper import set_and_get_session_key

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
        if prozdo_key is None and request.user.is_authenticated():
            prozdo_key = set_and_get_session_key(request.session)
        request.session.prozdo_key = prozdo_key