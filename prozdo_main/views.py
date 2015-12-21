from django.views import generic
from django.shortcuts import get_object_or_404
from django.http.response import HttpResponseRedirect
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from allauth.account.views import PasswordChangeView, PasswordResetView, PasswordResetDoneView, PasswordResetFromKeyView, PasswordResetFromKeyDoneView, ConfirmEmailView, EmailView
from django.db.models.aggregates import Count
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from allauth.account.models import EmailAddress
from allauth.socialaccount.views import SignupView as SocialSignupView, LoginCancelledView, LoginErrorView, ConnectionsView
from . import models, forms
from helper.helper import to_int
from django.contrib import messages
from django.utils import timezone
from cache.decorators import cached_view
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Case, Value, When, CharField
from super_model import models as super_models
from super_model import forms as super_forms
from super_model import helper as super_helper
from super_model import decorators as super_decorators
from super_model import views as super_views



class PostDetail(super_views.SuperListView):
    context_object_name = 'comments'
    paginate_by = settings.POST_COMMENTS_PAGE_SIZE
    template_name = 'prozdo_main/post/post_detail.html'

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

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
            comments = self.post.obj.comments.get_available().filter(parent=None)
        else:
            comments = self.post.obj.comments.get_available()
        if order_by_created == forms.COMMENTS_ORDER_BY_CREATED_DEC:
            comments = comments.order_by('-created')
        else:
            comments = comments.order_by('created')

        return comments

    @cached_view(test=super_models.request_with_empty_guest)
    def get(self, request, *args, **kwargs):
        self.set_obj()
        self.set_comment_page()
        res = super().get(request, *args, **kwargs)
        last_modified = self.obj.last_modified
        if last_modified:
            last_modified = super_helper.convert_date_for_last_modified(last_modified)
            expires = timezone.now() + timezone.timedelta(seconds=settings.CACHED_VIEW_DURATION)
            res['Last-Modified'] = last_modified
            res['Expires'] = super_helper.convert_date_for_last_modified(expires)
        return res

    @staticmethod
    def get_post(kwargs):
        if 'alias' in kwargs:
            alias = kwargs['alias']
            post = get_object_or_404(models.Post, alias=alias)
        else:
            pk = kwargs['pk']
            post = get_object_or_404(models.Post, pk=pk)
        return post

    def set_obj(self):
        post = self.get_post(self.kwargs)
        self.post = post
        self.obj = post.obj

    def set_comment_page(self):
        if self.kwargs['action'] == 'comment':
            try:
                comment = models.Comment.objects.get(pk=self.kwargs['comment_pk'])
                self.kwargs[self.page_kwarg] = comment.page
            except ObjectDoesNotExist:
                pass

    def get_context_data(self, comment_form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

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
        context['mark'] = self.post.obj.get_mark_by_request(request)

        if self.obj.is_blog:
            user_mark = self.obj.get_mark_blog_by_request(request)
            if user_mark == 0:
                context['can_mark_blog'] = True
            else:
                context['can_mark_blog'] = False


        #visibility
        if context['mark']:
            if user.is_authenticated():
                hist_exists = models.History.objects.filter(history_type=super_models.HISTORY_TYPE_POST_RATED, user=user, post=self.post, deleted=False).exists()
            else:
                hist_exists = models.History.objects.filter(history_type=super_models.HISTORY_TYPE_POST_RATED, session_key=getattr(request.session, settings.SUPER_MODEL_KEY_NAME), post=self.post, deleted=False).exists()
            if hist_exists:
                show_your_mark_block_cls = ''
                show_make_mark_block_cls = 'hidden'
            else:
                show_your_mark_block_cls = 'hidden'
                show_make_mark_block_cls = ''
        else:
            show_your_mark_block_cls = 'hidden'
            show_make_mark_block_cls = ''
        context['show_your_mark_block_cls'] = show_your_mark_block_cls
        context['show_make_mark_block_cls'] = show_make_mark_block_cls
        return context

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        user = request.user
        self.set_obj()
        self.object_list = self.get_queryset()
        comment_form = forms.CommentForm(request.POST, request=request, post=self.post)
        comment_form.instance.post = self.post
        comment_form.instance.ip = request.client_ip
        comment_form.instance.session_key = super_helper.set_and_get_session_key(request.session)
        if user.is_authenticated() and not comment_form.instance.user:
            comment_form.instance.user = user

        if comment_form.is_valid():
            comment_form.instance.status = comment_form.instance.get_status()
            comment = comment_form.save()
            published = comment.status == super_models.COMMENT_STATUS_PUBLISHED

            if not published:
                messages.add_message(request, messages.INFO, 'Ваш отзыв будет опубликован после проверки модератором')
            comment.send_confirmation_mail(request=request)

            #models.History.save_history(history_type=models.HISTORY_TYPE_COMMENT_CREATED, post=self.post, user=request.user, ip=request.client_ip, comment=comment)
            if request.is_ajax():
                return JsonResponse({'href': comment.get_absolute_url(), 'status': 1, 'published': published})
            else:
                return HttpResponseRedirect(self.obj.get_absolute_url())
        else:
            if request.is_ajax():
                return JsonResponse({'comment_form': comment_form.as_p(), 'status': 2})
            else:
                return self.render_to_response(self.get_context_data(comment_form=comment_form, **kwargs))


class PostViewMixin(super_views.SuperPostViewMixin):
    def set_model(self):
        if self.kwargs['post_type'] == 'drug':
            self.model =  models.Drug
        elif self.kwargs['post_type'] == 'cosmetics':
            self.model = models.Cosmetics
        elif self.kwargs['post_type'] == 'blog':
            self.model = models.Blog
        elif self.kwargs['post_type'] == 'component':
            self.model = models.Component


class PostListFilterMixin(super_views.SuperPostListFilterMixin, PostViewMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.model == models.Drug:
            context['post_type'] = 'drug'
        elif self.model == models.Cosmetics:
            context['post_type'] = 'cosmetics'
        elif self.model == models.Component:
            context['post_type'] = 'component'
        elif self.model == models.Blog:
            context['post_type'] = 'blog'
        context['list_view_default_template'] = self.model.list_view_default_template()
        return context

    def get_filter_form(self):
        if self.request.method.lower() == 'post':
            data = self.request.POST
        else:
            data = self.request.GET
        if self.model == models.Drug:
            if not hasattr(self, '_drug_filter_form'):
                self._drug_filter_form = forms.DrugFilterForm(data)
            return self._drug_filter_form
        elif self.model == models.Cosmetics:
            if not hasattr(self, '_cosmetics_filter_form'):
                self._cosmetics_filter_form = forms.CosmeticsFilterForm(data)
            return self._cosmetics_filter_form
        elif self.model == models.Component:
            if not hasattr(self, '_component_filter_form'):
                self._component_filter_form = forms.ComponentFilterForm(data)
            return self._component_filter_form
        else:
            return None


class PostList(PostListFilterMixin):
    template_name = 'prozdo_main/post/post_list.html'

    @cached_view(timeout=60 * 60 * 12, test=super_models.request_with_empty_guest)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = self.get_filter_form()
        context['ajax_submit_url'] = self.model.ajax_submit_url()
        context['submit_url'] = self.model.submit_url()
        return context


class PostListAjax(PostListFilterMixin):
    template_name = 'prozdo_main/post/_post_list_ajax.html'

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(**kwargs))


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
            context['show_as_child'] = True
            context['children'] = comment.get_children_tree
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


class CommentGetForAnswerToBlockAjax(generic.TemplateView):
    template_name =  'prozdo_main/comment/_comment_for_answer_block.html'

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.request.POST['pk']
        context['comment'] = models.Comment.objects.get(pk=pk)
        return context

    def post(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))


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

        user_pks = models.History.objects.filter(~Q(user=None), history_type=super_models.HISTORY_TYPE_COMMENT_RATED, comment=comment, deleted=False).values_list('user', flat=True)
        context['users'] = models.User.objects.filter(pk__in=user_pks)
        context['guest_count'] = models.History.objects.filter(user=None, history_type=super_models.HISTORY_TYPE_COMMENT_RATED, comment=comment, deleted=False).count()
        return context

    def post(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))


class MainPageView(generic.TemplateView):
    template_name = 'prozdo_main/base/main_page.html'

    @cached_view(timeout=60 * 60, test=super_models.request_with_empty_guest)
    def dispatch(self, request, *args, **kwargs):
        res = super().dispatch(request, *args, **kwargs)
        try:
            last_modified = models.History.objects.filter(history_type=models.HISTORY_TYPE_COMMENT_CREATED, deleted=False).latest('created').created
            res['Last-Modified'] = super_helper.convert_date_for_last_modified(last_modified)
            res['Expires'] = super_helper.convert_date_for_last_modified(last_modified + timezone.timedelta(seconds=60 * 60))
        except:
            pass

        return res

    def get_popular_drugs(self):
        drugs = models.Drug.objects.get_available().annotate(comment_count=Count('comments')).order_by('-comment_count')[:16]
        return drugs

    def get_recent_blogs(self):
        blogs = models.Blog.objects.get_available().order_by('-created')[:4]
        return blogs

    def get_recent_consults(self):
        comments = models.Comment.objects.get_available().filter(user__user_profile__role=settings.USER_ROLE_DOCTOR, parent__consult_required=True).order_by('-created')[:12]
        return comments

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popular_drugs'] = self.get_popular_drugs()
        recent_blogs = self.get_recent_blogs()
        if recent_blogs.exists():
            context['recent_blogs'] = recent_blogs[1:4]
            context['main_recent_blog'] = recent_blogs[0]
        context['recent_consults'] = self.get_recent_consults()
        return context

#*********************************<Account




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


class ProzdoSocialSignupView(SocialSignupView):
    template_name = 'prozdo_main/user/social/signup.html'

class ProzdoLoginCancelledView(LoginCancelledView):
    template_name = 'prozdo_main/user/social/login_cancelled.html'

class ProzdoLoginErrorView(LoginErrorView):
    template_name = 'prozdo_main/user/social/authentication_error.html'

class ProzdoConnectionsView(ConnectionsView):
    template_name = 'prozdo_main/user/social/connections.html'

    @super_decorators.login_required()
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

class ProzdoEmailView(EmailView):
    template_name = 'prozdo_main/user/email.html'


class ProzdoConfirmEmailView(ConfirmEmailView):
    def get_template_names(self):
        if self.request.method == 'POST':
            return ["prozdo_main/user/email_confirmed.html"]
        else:
            return ["prozdo_main/user/email_confirm.html"]

#*********************************Account>

class UserProfileView(generic.TemplateView):
    template_name = 'prozdo_main/user/user_profile.html'

    @super_decorators.login_required()
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, user_profile_form=None, user_form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_profile = self.request.user.user_profile
        context['user'] = user
        #context['user_profile'] = user_profile
        if user_profile_form is None:
            user_profile_form = super_forms.UserProfileForm(instance=user_profile)
        context['user_profile_form'] = user_profile_form

        if user_form is None:
            user_form = super_forms.UserForm(instance=user)
        context['user_form'] = user_form
        return context


    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        user = self.request.user
        user_profile = self.request.user.user_profile
        user_profile_form = super_forms.UserProfileForm(request.POST, request.FILES, instance=user_profile)
        user_form = super_forms.UserForm(request.POST,instance=user)
        if user_form.is_valid() and user_profile_form.is_valid():
            user_form.save()
            user_profile_form.save()
            messages.add_message(request, messages.INFO, 'Данные о пользователе изменены.')
            return HttpResponseRedirect(reverse_lazy('user-profile'))
        else:
            return self.render_to_response(self.get_context_data(user_profile_form=user_profile_form, user_form=user_form, **kwargs))


class UserDetailView(generic.TemplateView):
    template_name = 'prozdo_main/user/user_detail.html'

    @cached_view(timeout= 60 * 60 * 24, test=super_models.request_with_empty_guest)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        user = models.User.objects.get(pk=pk)
        context['current_user'] = user
        #context['comments'] = user.comments.get_available()
        return context


class UserCommentsView(super_views.SuperListView):
    template_name = 'prozdo_main/user/user_comments.html'
    context_object_name = 'comments'
    paginate_by = 50

    @cached_view(timeout= 60 * 60 * 24, test=super_models.request_with_empty_guest)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

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



class UserKarmaView(super_views.SuperListView):
    template_name = 'prozdo_main/user/user_karma.html'
    context_object_name = 'hists'
    paginate_by = 50

    #TODO переделать на инвалидацию и добавить заголовки. Пока сойтет так
    @cached_view(timeout= 60 * 60 * 24, test=super_models.request_with_empty_guest)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        pk = self.kwargs['pk']
        user = models.User.objects.get(pk=pk)
        return user.user_profile.karm_history()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        user = models.User.objects.get(pk=pk)
        context['current_user'] = user
        return context


class UserActivityView(super_views.SuperListView):
    template_name = 'prozdo_main/user/user_activity.html'
    context_object_name = 'hists'
    paginate_by = 50

    #TODO переделать на инвалидацию и добавить заголовки. Пока сойтет так
    @cached_view(timeout= 60 * 60 * 24, test=super_models.request_with_empty_guest)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        pk = self.kwargs['pk']
        user = models.User.objects.get(pk=pk)
        return user.activity_history


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        user = models.User.objects.get(pk=pk)
        context['current_user'] = user
        return context

class PostCreateUpdateMixin(super_views.restrict_by_role_mixin(settings.USER_ROLE_ADMIN), PostViewMixin):
    def get_form_class(self):
        if self.model == models.Drug:
            return forms.DrugForm
        elif self.model == models.Cosmetics:
            return forms.CosmeticsForm
        elif self.model == models.Blog:
            return forms.BlogForm
        elif self.model == models.Component:
            return forms.ComponentForm

class PostCreate(PostCreateUpdateMixin, generic.CreateView):
    template_name ='prozdo_main/post/post_create.html'


class PostUpdate(PostCreateUpdateMixin, generic.UpdateView):
    template_name ='prozdo_main/post/post_create.html'


class CommentUpdate(generic.UpdateView):
    model = models.Comment
    form_class = forms.CommentUpdateForm
    template_name = 'prozdo_main/comment/update.html'

    def post(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs['pk']
        comment = self.model.objects.get(pk=pk)
        if not user == comment.user:
            return HttpResponseRedirect(comment.get_absolute_url())
        form = self.form_class(request.POST, instance=comment)
        form.instance.updater = request.user
        form.instance.session_key = super_helper.set_and_get_session_key(request.session)
        comment = form.save()
        return HttpResponseRedirect(comment.get_absolute_url())


class CommentDoctorListView(super_views.SuperListView):
    template_name = 'prozdo_main/comment/comment_doctor_list_view.html'
    context_object_name = 'comments'
    paginate_by = 50

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not (user.is_doctor or user.is_admin):
            return HttpResponseRedirect(reverse_lazy('login'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = forms.CommentDoctorListFilterForm(self.request.GET)
        context['form'] = form
        return context

    def get_queryset(self):
        queryset = models.Comment.objects.get_available().order_by('-published', '-created')
        form = forms.CommentDoctorListFilterForm(self.request.GET)
        form.full_clean()
        consult_required = to_int(form.cleaned_data.get('consult_required', forms.BOOL_CHOICE_DEFAULT))
        consult_done = to_int(form.cleaned_data.get('consult_done', forms.BOOL_CHOICE_DEFAULT))
        consult_only = form.cleaned_data.get('consult_only')
        start_date = form.cleaned_data.get('start_date', None)
        end_date = form.cleaned_data.get('end_date', None)

        if consult_required == forms.BOOL_CHOICE_YES:
            queryset = queryset.filter(consult_required=True)
        elif consult_required == forms.BOOL_CHOICE_NO:
            queryset = queryset.filter(consult_required=False)

        if consult_only:
            queryset = queryset.filter(user__user_profile__role=settings.USER_ROLE_DOCTOR)

        if consult_done == forms.BOOL_CHOICE_YES:
            queryset = queryset.filter(children__user__user_profile__role=settings.USER_ROLE_DOCTOR)
        elif consult_done == forms.BOOL_CHOICE_NO:
            queryset = queryset.exclude(children__user__user_profile__role=settings.USER_ROLE_DOCTOR)

        if start_date:
            queryset = queryset.filter(created__gte=start_date)

        if end_date:
            queryset = queryset.filter(created__lte=end_date)


        return queryset


class UnsubscribeView(generic.View):

    def get(self, request, *args, **kwargs):
        email = kwargs['email']
        key_from_request = kwargs['key']
        email_address = EmailAddress.objects.get(email=email)
        try:
            key = email_address.emailconfirmation_set.latest('created').key
        except:
            key = None

        if key is not None and key == key_from_request:
            user = email_address.user
            user_profile = user.user_profile
            user_profile.receive_messages = False
            user_profile.save()
            messages.add_message(request, messages.INFO, 'Вы больше не будете получать сообщения с сайта Prozdo.ru')
            return HttpResponseRedirect(reverse_lazy('main-page'))



from haystack.generic_views import SearchView
from haystack.query import SearchQuerySet


class ProzdoSearchView(SearchView):
    queryset = SearchQuerySet().all()
    form_class = super_forms.SuperSearchForm

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by('weight')
        return queryset


class ProzdoAutocompleteView(generic.View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        q = request.POST.get('q', '').strip()
        if len(q) > 2:
            queryset = models.Post.objects.filter(title__icontains=q).annotate(
        entry_type=Case(
         When(post_type=settings.POST_TYPE_DRUG, then=Value(1)),
         When(post_type=settings.POST_TYPE_BLOG, then=Value(2)),
         When(post_type=settings.POST_TYPE_COSMETICS, then=Value(3)),
         When(post_type=settings.POST_TYPE_COMPONENT, then=Value(4)),
         default=Value(5),
         output_field=CharField(),
     )).annotate(comment_count=Count('comments')).order_by('-comment_count', 'entry_type')[:5]
            suggestions = [post.title for post in queryset]
        else:
            suggestions = []
        data = {
            'results': suggestions
        }
        return JsonResponse(data)

#class CommentConfirm(super_views.SuperCommentConfirm):
#    pass

#class CommentGetConfirmFormAjax(super_views.SuperCommentGetConfirmFormAjax):
#    pass


#class CommentDoConfirmAjax(super_views.SuperCommentDoConfirmAjax):
#    pass

#class GetAjaxLoginFormView(super_views.SuperGetAjaxLoginFormView):
#    pass


#class AjaxLoginView(super_views.SuperAjaxLoginView):
#    pass