from django.conf import settings
from .helper import get_client_ip

def debug(request):
    ip = get_client_ip(request)
    deb = settings.DEBUG or ip in settings.INTERNAL_IPS
    return {'debug': deb}


def show_ad(request):
    ip = get_client_ip(request)
    deb = settings.DEBUG or ip in settings.INTERNAL_IPS
    user = request.user
    return user.is_regular and not deb