from django.views import generic
from . import models, forms
from django.shortcuts import get_object_or_404
from django.http.response import HttpResponseRedirect
from .helper import get_client_ip
from django.db import transaction
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from allauth.account.views import SignupView, LoginView, LogoutView, PasswordChangeView, PasswordResetView, PasswordResetDoneView, PasswordResetFromKeyView, PasswordResetFromKeyDoneView
from django.db.models.aggregates import Sum, Count
from django.core.urlresolvers import reverse_lazy


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
        self.set_comment_page()
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

    def set_comment_page(self):
        if self.kwargs['action'] == 'comment':
            comment = models.Comment.objects.get(pk=self.kwargs['pk'])
            self.kwargs[self.page_kwarg] = comment.page

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
            comment_form = forms.CommentForm(request=self.request, post=self.post)
        context['comment_form'] = comment_form

        comments_options_form = forms.CommentsOptionsForm(self.request.GET)

        context['comments_options_form'] = comments_options_form

        context['mark'] = self.post.get_mark_by_request(request)

        return context

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        self.set_obj()
        self.object_list = self.get_queryset()
        comment_form = forms.CommentForm(request.POST, request=request, post=self.post)
        if comment_form.is_valid():
            comment_form.instance.post = self.post
            comment_form.instance.ip = get_client_ip(request)
            if request.user.is_authenticated():
                comment_form.instance.user = request.user
            comment_form.instance.status = comment_form.instance.get_status()
            comment = comment_form.save()
            #models.History.save_history(history_type=models.HISTORY_TYPE_COMMENT_CREATED, post=self.post, user=request.user, ip=get_client_ip(request), comment=comment)
            if request.is_ajax():
                return JsonResponse({'href': comment.get_absolute_url(), 'status': 1})
            else:
                return HttpResponseRedirect(self.obj.get_absolute_url())
        else:
            if request.is_ajax():
                return JsonResponse({'comment_form': comment_form.as_p(), 'status': 2})
            else:
                return self.render_to_response(self.get_context_data(comment_form=comment_form, **kwargs))


class DrugList(generic.ListView):
    template_name = 'prozdo_main/post/drug_list.html'
    model = models.Drug
    context_object_name = 'drugs'
    paginate_by = settings.DRUG_LIST_PAGE_SIZE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['drug_filter_form'] = self.get_drug_filter_form()
        return context

    def get_queryset(self):
        drug_filter_form = self.get_drug_filter_form()
        drug_filter_form.full_clean()
        dosage_forms = drug_filter_form.cleaned_data['dosage_forms']
        usage_areas = drug_filter_form.cleaned_data['usage_areas']
        queryset = super().get_queryset()
        if dosage_forms.exists():
            queryset = queryset.filter(dosage_forms__in=dosage_forms)
        if usage_areas.exists():
            queryset = queryset.filter(usage_areas__in=usage_areas)

        letter = self.kwargs.get('letter', None)
        if letter:
            queryset = queryset.filter(title__istartswith=letter)
        return queryset



    def get_drug_filter_form(self):
        if not hasattr(self, '_drug_filter_form'):
            self._drug_filter_form = forms.DrugFilterForm(self.request.GET)
        return self._drug_filter_form

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)



class HistoryAjaxSave(generic.View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pk = request.POST['pk']
        action = request.POST['action']
        ip = get_client_ip(request)
        user = request.user

        if action == 'comment-mark':
            comment = models.Comment.objects.get(pk=pk)
            models.History.save_history(history_type=models.HISTORY_TYPE_COMMENT_RATED, post=comment.post, user=request.user, comment=comment, ip=ip)
            return HttpResponse(comment.comment_mark)
        elif action == 'comment-unmark':
            comment = models.Comment.objects.get(pk=pk)
            if request.user.is_authenticated():
                models.History.objects.filter(history_type=models.HISTORY_TYPE_COMMENT_RATED, user=request.user, comment=comment).delete()
            else:
                models.History.objects.filter(history_type=models.HISTORY_TYPE_COMMENT_RATED, comment=comment, user=None).delete()
            return HttpResponse(comment.comment_mark)
        elif action == 'comment-complain':
            comment = models.Comment.objects.get(pk=pk)
            models.History.save_history(history_type=models.HISTORY_TYPE_COMMENT_COMPLAINT, post=comment.post, user=request.user, comment=comment, ip=ip)
            return HttpResponse(comment.complain_count)
        elif action == 'comment-uncomplain':
            comment = models.Comment.objects.get(pk=pk)
            if request.user.is_authenticated():
                models.History.objects.filter(history_type=models.HISTORY_TYPE_COMMENT_COMPLAINT, user=request.user, comment=comment).delete()
            else:
                models.History.objects.filter(history_type=models.HISTORY_TYPE_COMMENT_COMPLAINT, comment=comment, user=None).delete()
            return HttpResponse(comment.complain_count)

        elif action == 'post-mark':
            mark = request.POST.get('mark', None)
            post = models.Post.objects.get(pk=pk)
            models.History.save_history(history_type=models.HISTORY_TYPE_POST_RATED, post=post, user=request.user, mark=mark, ip=ip)
            data = {'average_mark': post.average_mark, 'marks_count':post.marks_count }
            return JsonResponse(data)

        elif action == 'post-unmark':
            post = models.Post.objects.get(pk=pk)
            if request.user.is_authenticated():
                models.History.objects.filter(user=user, history_type=models.HISTORY_TYPE_POST_RATED, post=post).delete()
            else:
                models.History.objects.filter(ip=ip, history_type=models.HISTORY_TYPE_POST_RATED, post=post, user=None).delete()
            data = {'average_mark': post.average_mark, 'marks_count':post.marks_count }
            return JsonResponse(data)



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


class CommentShowMarkedUsersAjax(generic.TemplateView):
    template_name = 'prozdo_main/comment/_comment_show_marked_users_ajax.html'

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        pk = request.POST['pk']
        comment = models.Comment.objects.get(pk=pk)

        user_pks = models.History.objects.filter(~Q(user=None), history_type=models.HISTORY_TYPE_COMMENT_RATED, comment=comment).values_list('user', flat=True)
        context['users'] = models.User.objects.filter(pk__in=user_pks)
        context['guest_count'] = models.History.objects.filter(user=None, history_type=models.HISTORY_TYPE_COMMENT_RATED, comment=comment).count()
        return context

    def post(self, request, *args, **kwargs):

        return self.render_to_response(self.get_context_data(**kwargs))




class MainPageView(generic.TemplateView):
    template_name = 'prozdo_main/base/main_page.html'

    def get_popular_drugs(self):
        drugs = models.Drug.objects.get_available().annotate(comment_count=Count('comments')).order_by('-comment_count')[:18]
        return drugs


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popular_drugs'] = self.get_popular_drugs()
        return context

#*********************************<Account

class ProzdoSignupView(SignupView):
    template_name = 'prozdo_main/user/signup.html'
    form_class = forms.ProzdoSignupForm

class ProzdoLoginView(LoginView):
    template_name = 'prozdo_main/user/login.html'
    #form_class = forms.ProzdoSignupForm


class ProzdoLogoutView(LogoutView):
    pass


class ProzdoPasswordChangeView(PasswordChangeView):
    template_name = 'prozdo_main/user/password_change.html'
    success_url = reverse_lazy("user-profile")

class ProzdoPasswordResetView(PasswordResetView):
    template_name = 'prozdo_main/user/password_reset.html'
    success_url = reverse_lazy("password-reset-done")

class ProzdoPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'prozdo_main/user/password_reset_done.html'



class ProzdoPasswordResetFromKeyView(PasswordResetFromKeyView):
    template_name = 'prozdo_main/user/password_reset_from_key.html'
    success_url = reverse_lazy('password-reset-from-key-done')


class ProzdoPasswordResetFromKeyDoneView(PasswordResetFromKeyDoneView):
    template_name = 'prozdo_main/user/password_reset_from_key_done.html'



#*********************************Account>


class UserProfileView(generic.TemplateView):
    template_name = 'prozdo_main/user/user_profile.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated():
            return HttpResponseRedirect(reverse_lazy('login'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_profile = self.request.user.user_profile
        context['user'] = user
        #context['user_profile'] = user_profile
        if form is None:
            form = forms.UserProfileForm(instance=user_profile)
        context['form'] = form
        return context


    def post(self, request, *args, **kwargs):
        user = self.request.user
        user_profile = self.request.user.user_profile
        form = forms.UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy('user-profile'))
        else:
            return self.render_to_response(self.get_context_data(form=form, **kwargs))


class UserDetailView(generic.TemplateView):
    template_name = 'prozdo_main/user/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        user = models.User.objects.get(pk=pk)
        context['current_user'] = user
        #context['comments'] = user.comments.get_available()
        return context


class UserCommentsView(generic.ListView):
    template_name = 'prozdo_main/user/user_comments.html'
    context_object_name = 'comments'
    paginate_by = 5

    def get_queryset(self):
        pk = self.kwargs['pk']
        user = models.User.objects.get(pk=pk)
        return user.comments.get_available().order_by('-created')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        user = models.User.objects.get(pk=pk)
        context['current_user'] = user

        return context

class UserKarmaView(generic.ListView):
    template_name = 'prozdo_main/user/user_karma.html'
    context_object_name = 'hists'
    paginate_by = 5

    def get_queryset(self):
        pk = self.kwargs['pk']
        user = models.User.objects.get(pk=pk)
        return user.karm_history


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        user = models.User.objects.get(pk=pk)
        context['current_user'] = user
        return context


def restrict_by_role_mixin(role):
    class RoleOnlyMixin:
        def dispatch(self, request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return HttpResponseRedirect('login')
            elif not user.user_profile.role == role:
                return HttpResponseRedirect('main-page')
            return super().dispatch(request, *args, **kwargs)
    return RoleOnlyMixin


class DrugCreate(restrict_by_role_mixin(models.USER_ROLE_ADMIN), generic.CreateView):
    template_name ='prozdo_main/post/drug_create.html'
    model = models.Drug
    form_class = forms.DrugForm


class DrugUpdate(restrict_by_role_mixin(models.USER_ROLE_ADMIN), generic.UpdateView):
    template_name ='prozdo_main/post/drug_create.html'
    model = models.Drug
    form_class = forms.DrugForm

