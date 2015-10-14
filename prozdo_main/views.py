from django.views import generic
from django.shortcuts import get_object_or_404
from django.http.response import HttpResponseRedirect
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from allauth.account.views import SignupView, LoginView, LogoutView, PasswordChangeView, PasswordResetView, PasswordResetDoneView, PasswordResetFromKeyView, PasswordResetFromKeyDoneView
from django.db.models.aggregates import Count
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from allauth.account.models import EmailAddress
from allauth.account.forms import LoginForm
from allauth.socialaccount.views import SignupView as SocialSignupView, LoginCancelledView, LoginErrorView, ConnectionsView
from . import models, forms
from .helper import get_client_ip, to_int


class ProzdoListView(generic.ListView):
    pages_to_show = 10
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_page = context['page_obj'].number
        total_pages = context['paginator'].num_pages
        page_range = context['paginator'].page_range
        if total_pages <= self.pages_to_show:
            short_page_range = page_range
        else:
            i = j = current_page
            short_page_range = [current_page]
            while len(short_page_range) < self.pages_to_show:
                i += 1
                j -= 1
                if i in page_range:
                    short_page_range.append(i)
                if j in page_range:
                    short_page_range.append(j)
            #_short_page_range = [i for i in range(current_page - self.pages_to_show + 1, current_page + self.pages_to_show + 1) if i > 0]
            #for i in _short_page_range:
            short_page_range = sorted(short_page_range)
        context['short_page_range'] = short_page_range
        if not 1 in short_page_range:
            context['show_first_page'] = True
        if not total_pages in short_page_range:
            context['show_last_page'] = True

        return context



class PostDetail(ProzdoListView):
    context_object_name = 'comments'
    paginate_by = settings.POST_COMMENTS_PAGE_SIZE
    template_name = 'prozdo_main/post/post_detail.html'


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

    #def get_template_names(self):
        #if self.obj.post_type == models.POST_TYPE_DRUG:
        #    return 'prozdo_main/post/drug_detail.html'
        #elif self.obj.post_type == models.POST_TYPE_COMPONENT:
        #    return 'prozdo_main/post/component_detail.html'
        #elif self.obj.post_type == models.POST_TYPE_BLOG:
        #    return 'prozdo_main/post/blog_detail.html'
        #elif self.obj.post_type == models.POST_TYPE_FORUM:
        #    return 'prozdo_main/post/forum_detail.html'
        #elif self.obj.post_type == models.POST_TYPE_COSMETICS:
        #    return 'prozdo_main/post/cosmetics_detail.html'

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
            comment = models.Comment.objects.get(pk=self.kwargs['comment_pk'])
            self.kwargs[self.page_kwarg] = comment.page

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
        context['mark'] = self.post.get_mark_by_request(request)

        if self.obj.is_blog:
            user_mark = self.obj.get_mark_blog_by_request(request)
            if user_mark == 0:
                context['can_mark_blog'] = True
            else:
                context['can_mark_blog'] = False


        #visibility
        if context['mark']:
            if user.is_authenticated():
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
        if comment_form.is_valid():
            comment_form.instance.post = self.post
            comment_form.instance.ip = get_client_ip(request)
            if user.is_authenticated() and not comment_form.instance.user:
                comment_form.instance.user = user
            comment_form.instance.status = comment_form.instance.get_status()

            comment = comment_form.save()
            published = comment.status == models.COMMENT_STATUS_PUBLISHED
            comment.send_confirmation_mail(request=request)
            #models.History.save_history(history_type=models.HISTORY_TYPE_COMMENT_CREATED, post=self.post, user=request.user, ip=get_client_ip(request), comment=comment)
            if request.is_ajax():
                return JsonResponse({'href': comment.get_absolute_url(), 'status': 1, 'published': published})
            else:
                return HttpResponseRedirect(self.obj.get_absolute_url())
        else:
            if request.is_ajax():
                return JsonResponse({'comment_form': comment_form.as_p(), 'status': 2})
            else:
                return self.render_to_response(self.get_context_data(comment_form=comment_form, **kwargs))


class PostViewMixin:
    def set_model(self):
        if self.kwargs['post_type'] == 'drug':
            self.model =  models.Drug
        elif self.kwargs['post_type'] == 'cosmetics':
            self.model = models.Cosmetics
        elif self.kwargs['post_type'] == 'blog':
            self.model = models.Blog
        elif self.kwargs['post_type'] == 'component':
            self.model = models.Component


    def dispatch(self, request, *args, **kwargs):
        self.set_model()
        return super().dispatch(request, args, **kwargs)


class PostListFilterMixin(PostViewMixin, ProzdoListView):
    context_object_name = 'objs'
    paginate_by = settings.POST_LIST_PAGE_SIZE

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

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

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_form = self.get_filter_form()
        if filter_form:
            filter_form.full_clean()
            flt = {}
            for field_name, field_value in filter_form.cleaned_data.items():
            #usage_areas = drug_filter_form.cleaned_data['usage_areas']
                if len(field_value) > 0: #не exists() поскольку может быть list для component_type
                    #TODO Переделать на custom lookup
                    if field_name == 'alphabet':
                        ids = ()
                        for letter in field_value:
                            cur_ids = self.model.objects.filter(title__istartswith=letter).values_list('id', flat=True)
                            ids += tuple(cur_ids)
                        flt['id__in'] = ids
                    elif isinstance(field_value, str):
                        flt[field_name + '__icontains'] = field_value
                    else:
                        flt[field_name + '__in'] = field_value
            queryset = queryset.filter(**flt)
        return queryset

    def get_filter_form(self):
        if self.request.method.lower() == 'post':
            d = self.request.POST
        else:
            d = self.request.GET
        if self.model == models.Drug:
            if not hasattr(self, '_drug_filter_form'):
                self._drug_filter_form = forms.DrugFilterForm(d)
            return self._drug_filter_form
        elif self.model == models.Cosmetics:
            if not hasattr(self, '_cosmetics_filter_form'):
                self._cosmetics_filter_form = forms.CosmeticsFilterForm(d)
            return self._cosmetics_filter_form
        elif self.model == models.Component:
            if not hasattr(self, '_component_filter_form'):
                self._component_filter_form = forms.ComponentFilterForm(d)
            return self._component_filter_form
        else:
            return None


class PostList(PostListFilterMixin):
    template_name = 'prozdo_main/post/post_list.html'

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


class HistoryAjaxSave(generic.View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pk = request.POST['pk']
        action = request.POST['action']
        ip = get_client_ip(request)
        user = request.user
        session_key = request.session.session_key

        if action == 'comment-mark':
            comment = models.Comment.objects.get(pk=pk)
            h = models.History.save_history(history_type=models.HISTORY_TYPE_COMMENT_RATED, post=comment.post, user=request.user, comment=comment, ip=ip, session_key=session_key)
            data = {'mark': comment.comment_mark}
            if h:
                data['saved'] = True
            else:
                data['saved'] = False
            return JsonResponse(data)
        elif action == 'comment-unmark':
            comment = models.Comment.objects.get(pk=pk)
            if request.user.is_authenticated():
                h = models.History.objects.filter(history_type=models.HISTORY_TYPE_COMMENT_RATED, user=request.user, comment=comment)
            else:
                h = models.History.objects.filter(history_type=models.HISTORY_TYPE_COMMENT_RATED, comment=comment, user=None, session_key=session_key)
                #if session_key:
                #    h = h.filter(Q(session_key=session_key)|Q(ip=ip))
                #else:
                #    h = h.filter(ip=ip)
            data = {}
            if h.exists():
                h.delete()
                data['saved'] = True
            else:
                data['saved'] = False
            data['mark'] = comment.comment_mark
            return JsonResponse(data)
        elif action == 'comment-complain':
            comment = models.Comment.objects.get(pk=pk)
            h = models.History.save_history(history_type=models.HISTORY_TYPE_COMMENT_COMPLAINT, post=comment.post, user=request.user, comment=comment, ip=ip, session_key=request.session.session_key)
            data = {'mark': comment.complain_count}
            if h:
                data['saved'] = True
            else:
                data['saved'] = False
            return JsonResponse(data)
        elif action == 'comment-uncomplain':
            comment = models.Comment.objects.get(pk=pk)
            if request.user.is_authenticated():
                h = models.History.objects.filter(history_type=models.HISTORY_TYPE_COMMENT_COMPLAINT, user=request.user, comment=comment)
            else:
                h = models.History.objects.filter(history_type=models.HISTORY_TYPE_COMMENT_COMPLAINT, comment=comment, user=None, session_key=session_key)
            data = {}
            if h.exists():
                h.delete()
                data['saved'] = True
            else:
                data['saved'] = False
            data['mark'] = comment.complain_count
            return JsonResponse(data)

        elif action == 'post-mark':
            mark = request.POST.get('mark', None)
            post = models.Post.objects.get(pk=pk)
            h = models.History.save_history(history_type=models.HISTORY_TYPE_POST_RATED, post=post, user=request.user, mark=mark, ip=ip, session_key=request.session.session_key)
            data = {}
            if h:
                data['saved'] = True
            else:
                data['saved'] = False
            data['average_mark'] = post.average_mark,
            data['marks_count'] = post.marks_count
            data['mark'] = post.get_mark_by_request(request)
            return JsonResponse(data)

        elif action == 'post-unmark':
            post = models.Post.objects.get(pk=pk)
            if request.user.is_authenticated():
                h = models.History.objects.filter(user=user, history_type=models.HISTORY_TYPE_POST_RATED, post=post)
            else:
                h = models.History.objects.filter(session_key=session_key, history_type=models.HISTORY_TYPE_POST_RATED, post=post, user=None)
            data = {}
            if h.exists():
                h.delete()
                data['saved'] = True
            else:
                data['saved'] = False
            data['average_mark'] = post.average_mark,
            data['marks_count'] = post.marks_count
            data['mark'] = 0
            return JsonResponse(data)

        """
        elif action == 'blog-mark':
            post = models.Post.objects.get(pk=pk)
            blog = post.obj
            h = models.History.save_history(history_type=models.HISTORY_TYPE_POST_RATED, post=post, user=request.user, ip=ip, session_key=request.session.session_key)
            data = {}
            if h:
                data['saved'] = True
            else:
                data['saved'] = False

            data = {'mark': blog.mark}

            if h:
                data['saved'] = True
            else:
                data['saved'] = False

            return JsonResponse(data)
        """

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
            context['children'] = comment.get_children_tree()
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


class CommentGetConfirmFormAjax(generic.TemplateView):
    template_name = 'prozdo_main/comment/_get_confirm_form.html'
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.request.POST['pk']
        comment = models.Comment.objects.get(pk=pk)
        form = forms.CommentConfirmForm(initial={'comment': comment})
        context['form'] = form
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        pk = self.request.POST['pk']
        comment = models.Comment.objects.get(pk=pk)
        if user.is_authenticated():
            try:
                email = EmailAddress.objects.get(user=user)
            except:
                email= None
            if email and email.verified and user.email == comment.email:
                comment.confirmed = True
                comment.save()
                return HttpResponse('Отзыв подтвержден')

        return self.render_to_response(self.get_context_data(**kwargs))

class CommentDoConfirmAjax(generic.TemplateView):
    template_name = 'prozdo_main/comment/_get_confirm_form.html'
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = request.user
        form = forms.CommentConfirmForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data['comment']

            if user.is_authenticated():
                try:
                    email = EmailAddress.objects.get(user=user)
                except:
                    email= None
                if email and email.verified and user.email == comment.email:
                    comment.confirmed = True
                    comment.save()
                    return HttpResponse('Отзыв подтвержден')
            email = form.cleaned_data['email']
            if comment.email == email:
                comment.send_confirmation_mail(request=request)
                return HttpResponse('На Ваш адрес электронной почту отправлено сообщение с дальнейшими инструкциями')
            else:
                form.add_error('email', 'Адрес электронной почты указан неверно')
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)






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

        user_pks = models.History.objects.filter(~Q(user=None), history_type=models.HISTORY_TYPE_COMMENT_RATED, comment=comment).values_list('user', flat=True)
        context['users'] = models.User.objects.filter(pk__in=user_pks)
        context['guest_count'] = models.History.objects.filter(user=None, history_type=models.HISTORY_TYPE_COMMENT_RATED, comment=comment).count()
        return context

    def post(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))


class MainPageView(generic.TemplateView):
    template_name = 'prozdo_main/base/main_page.html'

    def get_popular_drugs(self):
        drugs = models.Drug.objects.get_available().annotate(comment_count=Count('comments')).order_by('-comment_count')[:16]
        return drugs

    def get_recent_blogs(self):
        blogs = models.Blog.objects.get_available().order_by('-created')[:4]
        return blogs

    def get_recent_consults(self):
        comments = models.Comment.objects.get_available().filter(user__user_profile__role=models.USER_ROLE_DOCTOR, parent__consult_required=True).order_by('-created')[:12]
        return comments

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popular_drugs'] = self.get_popular_drugs()
        context['recent_blogs'] = self.get_recent_blogs()[1:4]
        context['main_recent_blog'] = self.get_recent_blogs()[0]
        context['recent_consults'] = self.get_recent_consults()
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


class ProzdoSocialSignupView(SocialSignupView):
    template_name = 'prozdo_main/user/social/signup.html'

class ProzdoLoginCancelledView(LoginCancelledView):
    template_name = 'prozdo_main/user/social/login_cancelled.html'

class ProzdoLoginErrorView(LoginErrorView):
    template_name = 'prozdo_main/user/social/authentication_error.html'

class ProzdoConnectionsView(ConnectionsView):
    template_name = 'prozdo_main/user/social/connections.html'



#*********************************Account>

class UserProfileView(generic.TemplateView):
    template_name = 'prozdo_main/user/user_profile.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated():
            return HttpResponseRedirect(reverse_lazy('login'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, user_profile_form=None, user_form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_profile = self.request.user.user_profile
        context['user'] = user
        #context['user_profile'] = user_profile
        if user_profile_form is None:
            user_profile_form = forms.UserProfileForm(instance=user_profile)
        context['user_profile_form'] = user_profile_form

        if user_form is None:
            user_form = forms.UserForm(instance=user)
        context['user_form'] = user_form
        return context


    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        user = self.request.user
        user_profile = self.request.user.user_profile
        user_profile_form = forms.UserProfileForm(request.POST, request.FILES, instance=user_profile)
        user_form = forms.UserForm(request.POST,instance=user)
        if user_form.is_valid() and user_profile_form.is_valid():
            user_form.save()
            user_profile_form.save()
            return HttpResponseRedirect(reverse_lazy('user-profile'))
        else:
            return self.render_to_response(self.get_context_data(user_profile_form=user_profile_form, user_form=user_form, **kwargs))


class UserDetailView(generic.TemplateView):
    template_name = 'prozdo_main/user/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        user = models.User.objects.get(pk=pk)
        context['current_user'] = user
        #context['comments'] = user.comments.get_available()
        return context


class UserCommentsView(ProzdoListView):
    template_name = 'prozdo_main/user/user_comments.html'
    context_object_name = 'comments'
    paginate_by = 50

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



class UserKarmaView(ProzdoListView):
    template_name = 'prozdo_main/user/user_karma.html'
    context_object_name = 'hists'
    paginate_by = 50

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


class UserActivityView(ProzdoListView):
    template_name = 'prozdo_main/user/user_activity.html'
    context_object_name = 'hists'
    paginate_by = 50

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


def restrict_by_role_mixin(role):
    class RoleOnlyMixin():
        def dispatch(self, request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated():
                return HttpResponseRedirect(reverse_lazy('login'))
            elif not user.user_profile.role == role:
                return HttpResponseRedirect('main-page')
            return super().dispatch(request, *args, **kwargs)
    return RoleOnlyMixin



class PostCreateUpdateMixin(restrict_by_role_mixin(models.USER_ROLE_ADMIN), PostViewMixin):
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


class CommentConfirm(generic.TemplateView):
    template_name = 'prozdo_main/comment/confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            comment_pk = kwargs['comment_pk']
            key = kwargs['key']
            comment = models.Comment.objects.get(pk=comment_pk, key=key)
            if comment.confirmed == False:
                comment.confirmed = True
                comment.save()
                context['saved'] = True
            else:
                context['not_saved'] = True

        except:
            context['not_found'] = True
        return context


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
        comment = form.save()
        return HttpResponseRedirect(comment.get_absolute_url())


class CommentDoctorListView(ProzdoListView):
    template_name = 'prozdo_main/comment/comment_doctor_list_view.html'
    context_object_name = 'comments'
    paginate_by = 50

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not (user.is_doctor or user.is_admin):
            return HttpResponseRedirect('login')
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
            queryset = queryset.filter(user__user_profile__role=models.USER_ROLE_DOCTOR)

        if consult_done == forms.BOOL_CHOICE_YES:
            queryset = queryset.filter(children__user__user_profile__role=models.USER_ROLE_DOCTOR)
        elif consult_done == forms.BOOL_CHOICE_NO:
            queryset = queryset.exclude(children__user__user_profile__role=models.USER_ROLE_DOCTOR)

        if start_date:
            queryset = queryset.filter(created__gte=start_date)

        if end_date:
            queryset = queryset.filter(created__lte=end_date)


        return queryset


class GetAjaxLoginFormView(generic.TemplateView):
    template_name = 'prozdo_main/user/_ajax_login.html'

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = LoginForm()
        return context


    def post(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))


class AjaxLoginView(LoginView):
    template_name = 'prozdo_main/user/_ajax_login.html'

