from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db.models import Case, Value, When, CharField
from django.db.models.aggregates import Count
from django.http import JsonResponse
from django.http.response import HttpResponseRedirect
from django.utils import timezone
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from cache.decorators import cached_view
from helper.helper import to_int
from super_model import forms as super_forms
from super_model import helper as super_helper
from super_model import models as super_models
from super_model import views as super_views
from . import models, forms


class PostDetail(super_views.SuperPostDetail):
    template_name = 'main/post/post_detail.html'
    comment_form = forms.CommentForm
    comment_options_form = forms.CommentOptionsForm

    @cached_view(test=super_models.request_with_empty_guest, model_class=models.Post, kwarg='alias')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PostViewMixin(super_views.SuperPostViewMixin):
    def set_model(self):
        if self.kwargs['post_type'] == 'drug':
            self.model = models.Drug
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
    template_name = 'main/post/post_list.html'

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
    template_name = 'main/post/_post_list_ajax.html'

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(**kwargs))


class CommentGetForAnswerToBlockAjax(generic.TemplateView):
    template_name = 'main/comment/_comment_for_answer_block.html'

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


class MainPageView(generic.TemplateView):
    template_name = 'main/base/main_page.html'

    @cached_view(timeout=60 * 60, test=super_models.request_with_empty_guest)
    def dispatch(self, request, *args, **kwargs):
        res = super().dispatch(request, *args, **kwargs)
        try:
            last_modified = models.History.objects.filter(history_type=super_models.HISTORY_TYPE_COMMENT_CREATED,
                                                          deleted=False).latest('created').created
            res['Last-Modified'] = super_helper.convert_date_for_last_modified(last_modified)
            res['Expires'] = super_helper.convert_date_for_last_modified(
                last_modified + timezone.timedelta(seconds=60 * 60))
        except:
            pass

        return res

    def get_popular_drugs(self):
        drugs = models.Drug.objects.get_available().annotate(comment_count=Count('comments')).order_by(
            '-comment_count')[:16]
        return drugs

    def get_recent_blogs(self):
        blogs = models.Blog.objects.get_available().order_by('-created')[:4]
        return blogs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popular_drugs'] = self.get_popular_drugs()
        recent_blogs = self.get_recent_blogs()
        if recent_blogs.exists():
            context['recent_blogs'] = recent_blogs[1:4]
            context['main_recent_blog'] = recent_blogs[0]
        return context


# *********************************<Account




# *********************************Account>


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
    template_name = 'main/post/post_create.html'


class PostUpdate(PostCreateUpdateMixin, generic.UpdateView):
    template_name = 'main/post/post_create.html'


class CommentUpdate(generic.UpdateView):
    model = models.Comment
    form_class = forms.CommentUpdateForm
    template_name = 'main/comment/update.html'

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
    template_name = 'main/comment/comment_doctor_list_view.html'
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
            queryset = models.Post.objects.get_available().filter(title__icontains=q).annotate(
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


# class CommentConfirm(super_views.SuperCommentConfirm):
#    pass

# class CommentGetConfirmFormAjax(super_views.SuperCommentGetConfirmFormAjax):
#    pass


# class CommentDoConfirmAjax(super_views.SuperCommentDoConfirmAjax):
#    pass

# class GetAjaxLoginFormView(super_views.SuperGetAjaxLoginFormView):
#    pass


# class AjaxLoginView(super_views.SuperAjaxLoginView):
#    pass

class CommentGetTreeAjax(super_views.SuperCommentGetTreeAjax):
    template_name = 'main/widgets/_get_child_comments.html'
