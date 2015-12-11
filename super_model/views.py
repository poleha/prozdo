from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy


def restrict_by_role_mixin(*roles):
    class RoleOnlyMixin:
        def dispatch(self, request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated():
                return HttpResponseRedirect(reverse_lazy('login'))
            elif not user.user_profile.role in roles:
                return HttpResponseRedirect(reverse_lazy('main-page'))
            return super().dispatch(request, *args, **kwargs)
    return RoleOnlyMixin