from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from . import helper
from django.utils.module_loading import import_string
from .app_settings import settings
from super_model import models

Comment = import_string(settings.BASE_COMMENT_CLASS)
History = import_string(settings.BASE_HISTORY_CLASS)
Post = import_string(settings.BASE_POST_CLASS)


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



class HistoryAjaxSave(generic.View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('pk', None)
        action = request.POST.get('action', None)

        if not pk or not action:
            data = {'saved': False}
            return JsonResponse(data)

        ip = request.client_ip
        user = request.user
        session_key = helper.set_and_get_session_key(request.session)

        if action == 'comment-mark':
            comment = Comment.objects.get(pk=pk)
            h = History.save_history(history_type=models.HISTORY_TYPE_COMMENT_RATED, post=comment.post, user=request.user, comment=comment, ip=ip, session_key=session_key)
            data = {'mark': comment.comment_mark}
            if h:
                data['saved'] = True
            else:
                data['saved'] = False
            return JsonResponse(data)
        elif action == 'comment-unmark':
            comment = Comment.objects.get(pk=pk)
            if request.user.is_authenticated():
                hs = History.objects.filter(history_type=models.HISTORY_TYPE_COMMENT_RATED, user=request.user, comment=comment, deleted=False)
            else:
                hs = History.objects.filter(history_type=models.HISTORY_TYPE_COMMENT_RATED, comment=comment, user=None, session_key=session_key, deleted=False)
                #if session_key:
                #    h = h.filter(Q(session_key=session_key)|Q(ip=ip))
                #else:
                #    h = h.filter(ip=ip)
            data = {}
            if hs.exists():
                for h in hs:
                    h.deleted = True
                    h.save()
                data['saved'] = True
            else:
                data['saved'] = False
            data['mark'] = comment.comment_mark
            return JsonResponse(data)
        elif action == 'comment-complain':
            comment = Comment.objects.get(pk=pk)
            h = History.save_history(history_type=models.HISTORY_TYPE_COMMENT_COMPLAINT, post=comment.post, user=request.user, comment=comment, ip=ip, session_key=session_key)
            data = {'mark': comment.complain_count}
            if h:
                data['saved'] = True
            else:
                data['saved'] = False
            return JsonResponse(data)
        elif action == 'comment-uncomplain':
            comment = Comment.objects.get(pk=pk)
            if request.user.is_authenticated():
                hs = History.objects.filter(history_type=models.HISTORY_TYPE_COMMENT_COMPLAINT, user=request.user, comment=comment, deleted=False)
            else:
                hs = History.objects.filter(history_type=models.HISTORY_TYPE_COMMENT_COMPLAINT, comment=comment, user=None, session_key=session_key, deleted=False)
            data = {}
            if hs.exists():
                for h in hs:
                    h.deleted = True
                    h.save()
                data['saved'] = True
            else:
                data['saved'] = False
            data['mark'] = comment.complain_count
            return JsonResponse(data)

        elif action == 'post-mark':
            mark = request.POST.get('mark', None)
            post = Post.objects.get(pk=pk)
            h = History.save_history(history_type=models.HISTORY_TYPE_POST_RATED, post=post, user=request.user, mark=mark, ip=ip, session_key=session_key)
            data = {}
            if h:
                data['saved'] = True
            else:
                data['saved'] = False
            data['average_mark'] = post.obj.average_mark,
            data['marks_count'] = post.obj.marks_count
            data['mark'] = post.get_mark_by_request(request)
            return JsonResponse(data)

        elif action == 'post-unmark':
            post = Post.objects.get(pk=pk)
            if request.user.is_authenticated():
                hs = History.objects.filter(user=user, history_type=models.HISTORY_TYPE_POST_RATED, post=post, deleted=False)
            else:
                hs = History.objects.filter(session_key=session_key, history_type=models.HISTORY_TYPE_POST_RATED, post=post, user=None, deleted=False)
            data = {}
            if hs.exists():
                for h in hs:
                    h.deleted = True
                    h.save()
                data['saved'] = True
            else:
                data['saved'] = False
            data['average_mark'] = post.obj.average_mark,
            data['marks_count'] = post.obj.marks_count
            data['mark'] = 0
            return JsonResponse(data)

        elif action == 'comment-delete':
            if not user.is_regular:
                comment = Comment.objects.get(pk=pk)
                if not comment.delete_mark:
                    comment.delete_mark = True
                    if not comment.session_key:
                        comment.session_key = session_key
                    comment.save()
                    return JsonResponse({'saved': True})
            return JsonResponse({'saved': False})

        elif action == 'comment-undelete':
            if not user.is_regular:
                comment = Comment.objects.get(pk=pk)
                if comment.delete_mark:
                    comment.delete_mark = False
                    comment.save()
                    return JsonResponse({'saved': True})
            return JsonResponse({'saved': False})