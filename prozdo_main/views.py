from django.views import generic
from . import models, forms
from django.shortcuts import get_object_or_404
from django.http.response import HttpResponseRedirect
from .helper import get_client_ip
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
#from django.utils.decorators import method_decorator
from django.conf import settings
from prozdo_main.helper import cut_text

class PostDetail(generic.ListView):
    context_object_name = 'comments'
    paginate_by = settings.POST_COMMENTS_PAGE_SIZE

    def get_queryset(self):
        request = self.request
        try:
            show_type = int(request.GET.get('show_type', forms.COMMENTS_SHOW_TYPE_PLAIN))
        except:
            show_type = forms.COMMENTS_SHOW_TYPE_PLAIN
        try:
            order_by_created = int(request.GET.get('order_by_created', forms.COMMENTS_ORDER_BY_CREATED_DEC))
        except:
            order_by_created = forms.COMMENTS_ORDER_BY_CREATED_DEC

        if show_type == forms.COMMENTS_SHOW_TYPE_TREE:
            comments = self.post.comments.filter(status=models.COMMENT_STATUS_PUBLISHED, parent=None)
        else:
            comments = self.post.comments.filter(status=models.COMMENT_STATUS_PUBLISHED)
        if order_by_created == forms.COMMENTS_ORDER_BY_CREATED_DEC:
            comments = comments.order_by('-created')
        else:
            comments = comments.order_by('created')

        return comments

    def get_template_names(self):
        if self.obj.post_type == models.POST_TYPE_DRUG:
            return 'prozdo_main/post/drug_detail.html'
        elif self.obj.post_type == models.POST_TYPE_COMPONENT:
            return 'prozdo_main/post/component_detail.html'
        elif self.obj.post_type == models.POST_TYPE_BLOG:
            return 'prozdo_main/post/blog_detail.html'
        elif self.obj.post_type == models.POST_TYPE_FORUM:
            return 'prozdo_main/post/forum_detail.html'
        elif self.obj.post_type == models.POST_TYPE_COSMETICS:
            return 'prozdo_main/post/cosmetics_detail.html'

    def get(self, request, *args, **kwargs):
        self.set_obj()
        return super().get(request, *args, **kwargs)


    def set_obj(self):
        if 'alias' in self.kwargs:
            alias = self.kwargs['alias']
            post = get_object_or_404(models.Post, alias=alias)
        else:
            pk = self.kwargs['pk']
            post = get_object_or_404(models.Post, pk=pk)
        self.post = post
        self.obj = post.obj

    def get_context_data(self, comment_form=None, **kwargs):
        context = super().get_context_data(**kwargs)

        request = self.request
        try:
            show_type = int(request.GET.get('show_type', forms.COMMENTS_SHOW_TYPE_PLAIN))
        except:
            show_type = forms.COMMENTS_SHOW_TYPE_PLAIN

        if show_type == forms.COMMENTS_SHOW_TYPE_TREE:
            context['show_tree'] = True

        else:
            context['show_tree'] = False

        context['obj'] = self.obj

        if comment_form is None:
            comment_form = forms.CommentForm(user=self.request.user, post=self.post)
        context['comment_form'] = comment_form

        comments_options_form = forms.CommentsOptionsForm(self.request.GET)

        context['comments_options_form'] = comments_options_form


        return context

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        self.set_obj()
        self.object_list = self.get_queryset()
        comment_form = forms.CommentForm(request.POST, user=request.user, post=self.post)
        if comment_form.is_valid():
            comment_form.instance.post = self.post
            comment_form.instance.ip = get_client_ip(request)
            if request.user.is_authenticated():
                comment_form.instance.user = request.user
            comment_form.instance.status = comment_form.instance.get_status()
            comment = comment_form.save()
            #models.History.save_history(history_type=models.HISTORY_TYPE_COMMENT_CREATED, post=self.post, user=request.user, ip=get_client_ip(request), comment=comment)
            return HttpResponseRedirect(self.obj.get_absolute_url())
        else:
            return self.render_to_response(self.get_context_data(comment_form=comment_form, **kwargs))



class DrugList(generic.ListView):
    template_name = 'prozdo_main/post/drug_list.html'
    model = models.Drug
    context_object_name = 'drugs'



class HistoryAjaxSave(generic.View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pk = request.POST['pk']
        action = request.POST['action']

        if action == 'comment-mark':
            comment = models.Comment.objects.get(pk=pk)
            models.History.save_history(history_type=models.HISTORY_TYPE_COMMENT_RATED, post=comment.post, user=request.user, comment=comment)
            return HttpResponse(comment.comment_mark)
        elif action == 'comment-unmark':
            comment = models.Comment.objects.get(pk=pk)
            if request.user.is_authenticated():
                models.History.objects.filter(history_type=models.HISTORY_TYPE_COMMENT_RATED, user=request.user, comment=comment).delete()
            else:
                models.History.objects.filter(history_type=models.HISTORY_TYPE_COMMENT_RATED, comment=comment).delete()
            return HttpResponse(comment.comment_mark)
        elif action == 'comment-complain':
            comment = models.Comment.objects.get(pk=pk)
            models.History.save_history(history_type=models.HISTORY_TYPE_COMMENT_COMPLAINT, post=comment.post, user=request.user, comment=comment)
            return HttpResponse(comment.complain_count)
        elif action == 'comment-uncomplain':
            comment = models.Comment.objects.get(pk=pk)
            if request.user.is_authenticated():
                models.History.objects.filter(history_type=models.HISTORY_TYPE_COMMENT_COMPLAINT, user=request.user, comment=comment).delete()
            else:
                models.History.objects.filter(history_type=models.HISTORY_TYPE_COMMENT_COMPLAINT, comment=comment).delete()
            return HttpResponse(comment.complain_count)


class CommentGetTreeAjax(generic.TemplateView):
    template_name = 'prozdo_main/widgets/_get_child_comments.html'

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.request.POST['pk']
        comment = models.Comment.objects.get(pk=pk)
        action = self.request.POST['action']

        if action == 'comment-tree-show':
            childs_list = comment.get_childs_tree()
            context['show_tree'] = False
            context['childs'] = childs_list
        return context

    def post(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))


class CommentGetTinyAjax(generic.View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        pk = self.request.POST['pk']
        action = self.request.POST['action']
        comment = models.Comment.objects.get(pk=pk)
        if action == 'show':
            res = comment.body
        else:
            res = comment.short_body
        return HttpResponse(res)