from django.conf.urls import url
from . import views
from .feed import LatestBlogEntriesFeed
#from django.views.decorators.cache import cache_page

urlpatterns = [
    #url(r'^drug/detail/(?P<pk>\d+)$', views.DrugDetail.as_view(), name='drug-detail'),
    url(r'^drug/list/$', views.PostList.as_view(), name='drug-list', kwargs={'post_type': 'drug'}),
    #url(r'^drug/list/letter/(?P<letter>[a-zа-я0-9])$', views.PostList.as_view(), kwargs={'action': 'alphabet', 'post_type': 'drug'}, name='drug-list-letter'),
    url(r'^drug/create/$', views.PostCreate.as_view(), name='drug-create', kwargs={'post_type': 'drug'}),
    url(r'^drug/update/(?P<pk>\d+)/$', views.PostUpdate.as_view(), name='drug-update', kwargs={'post_type': 'drug'}),
    url(r'^drug/list_ajax/$', views.PostListAjax.as_view(), name='drug-list-ajax', kwargs={'post_type': 'drug'}),

    url(r'^cosmetics/list/$', views.PostList.as_view(), name='cosmetics-list', kwargs={'post_type': 'cosmetics'}),
    #url(r'^cosmetics/list/letter/(?P<letter>[a-zа-я0-9])$', views.PostList.as_view(), kwargs={'action': 'alphabet', 'post_type': 'cosmetics'}, name='cosmetics-list-letter'),
    url(r'^cosmetics/create/$', views.PostCreate.as_view(), name='cosmetics-create', kwargs={'post_type': 'cosmetics'}),
    url(r'^cosmetics/update/(?P<pk>\d+)/$', views.PostUpdate.as_view(), name='cosmetics-update', kwargs={'post_type': 'cosmetics'}),
    url(r'^cosmetics/list_ajax/$', views.PostListAjax.as_view(), name='cosmetics-list-ajax', kwargs={'post_type': 'cosmetics'}),

    url(r'^blog/list/$', views.PostList.as_view(), name='blog-list', kwargs={'post_type': 'blog'}),
    url(r'^blog/create/$', views.PostCreate.as_view(), name='blog-create', kwargs={'post_type': 'blog'}),
    url(r'^blog/update/(?P<pk>\d+)/$', views.PostUpdate.as_view(), name='blog-update', kwargs={'post_type': 'blog'}),
    url(r'^blog/list_ajax/$', views.PostListAjax.as_view(), name='blog-list-ajax', kwargs={'post_type': 'blog'}),

    url(r'^component/list/$', views.PostList.as_view(), name='component-list', kwargs={'post_type': 'component'}),
    #url(r'^component/list/letter/(?P<letter>[a-zа-я0-9])$', views.PostList.as_view(), kwargs={'action': 'alphabet', 'post_type': 'component'}, name='component-list-letter'),
    url(r'^component/create/$', views.PostCreate.as_view(), name='component-create', kwargs={'post_type': 'component'}),
    url(r'^component/update/(?P<pk>\d+)/$', views.PostUpdate.as_view(), name='component-update', kwargs={'post_type': 'component'}),
    url(r'^component/list_ajax/$', views.PostListAjax.as_view(), name='component-list-ajax', kwargs={'post_type': 'component'}),

    url(r'^post/(?P<pk>\d+)/$', views.PostDetail.as_view(), kwargs={'action': 'normal'}, name='post-detail-pk'),
    url(r'^post/(?P<pk>\d+)/comment/(?P<comment_pk>\d+)/$', views.PostDetail.as_view(), kwargs={'action': 'comment'}, name='post-detail-pk-comment'),

    url(r'^comment/get_tree_ajax/$', views.CommentGetTreeAjax.as_view(), name='get-comment-tree-ajax'),

    url(r'^comment/(?P<comment_pk>\d+)/confirm/(?P<key>[a-z0-9_./]{1,})/$', views.CommentConfirm.as_view(), name='comment-confirm'),

    url(r'^comment/get_tiny_ajax/$', views.CommentGetTinyAjax.as_view(), name='comment-get-tiny-ajax'),

    url(r'^comment/get_for_answer_block_ajax/$', views.CommentGetForAnswerToBlockAjax.as_view(), name='comment-get-for-answer-block-ajax'),

    url(r'^comment/show_marked_users_ajax/$', views.CommentShowMarkedUsersAjax.as_view(), name='comment-show-marked-users-ajax'),

    url(r'^comment/get_confirm_form_ajax/$', views.CommentGetConfirmFormAjax.as_view(), name='comment-get-confirm-form-ajax'),
    url(r'^comment/do_confirm_ajax/$', views.CommentDoConfirmAjax.as_view(), name='comment-do-confirm-ajax'),

    url(r'^comment/update/(?P<pk>\d+)/$', views.CommentUpdate.as_view(), name='comment-update'),


    url(r'^comment/doctor_list/$', views.CommentDoctorListView.as_view(), name='comment-doctor-list'),


    url(r'^signup/$', views.ProzdoSignupView.as_view(), name='signup'),
    url(r'^login/$', views.ProzdoLoginView.as_view(), name='login'),
    url(r'^logout/$', views.ProzdoLogoutView.as_view(), name='logout'),
    url(r'^password_change/$', views.ProzdoPasswordChangeView.as_view(), name='password-change'),
    url(r'^password_reset/$', views.ProzdoPasswordResetView.as_view(), name='password-reset'),
    url(r'^password_reset_done/$', views.ProzdoPasswordResetDoneView.as_view(), name='password-reset-done'),
    url(r"^password_reset_from_key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        views.ProzdoPasswordResetFromKeyView.as_view(),
        name="password-reset-from-key"),
    url(r"^password_reset_from_key_done/$", views.ProzdoPasswordResetFromKeyDoneView.as_view(),
        name="password-reset-from-key-done"),

    url(r'^user_profile/$', views.UserProfileView.as_view(), name='user-profile'),
    url(r'^user/(?P<pk>\d+)/$', views.UserDetailView.as_view(), name='user-detail'),
    url(r'^user/comments/(?P<pk>\d+)/$', views.UserCommentsView.as_view(), name='user-comments'),
    url(r'^user/karma/(?P<pk>\d+)/$', views.UserKarmaView.as_view(), name='user-karma'),
    url(r'^user/activity/(?P<pk>\d+)/$', views.UserActivityView.as_view(), name='user-activity'),
    url(r'^unsubscribe/(?P<email>[0-9a-zA-Z.\-_@]+)/(?P<key>[0-9A-Za-z]+)/$', views.UnsubscribeView.as_view(), name='unsubscribe'),

    url(r'^get_ajax_login_form/$', views.GetAjaxLoginFormView.as_view(), name='get-ajax-login-form'),
    url(r'^ajax_login/$', views.AjaxLoginView.as_view(), name='ajax-login'),

    url(r"^email/$", views.ProzdoEmailView.as_view(), name="account_email"),
    url(r"^confirm-email/(?P<key>\w+)/$", views.ProzdoConfirmEmailView.as_view(), name="account_confirm_email"),
    #social
    url(r'^social_login/$', views.ProzdoSocialSignupView.as_view(), name='socialaccount_signup'), #Перекрываем их url. Иначе не получилось.
    url(r'^login_cancelled/$', views.ProzdoLoginCancelledView.as_view(),
        name='socialaccount_login_cancelled'),
    url(r'^login_error/$', views.ProzdoLoginErrorView.as_view(), name='socialaccount_login_error'),
    url(r'^connections/$', views.ProzdoConnectionsView.as_view(), name='socialaccount_connections'),


    url(r'^$', views.MainPageView.as_view(), name='main-page'),


    url(r'^rss/rss/$', LatestBlogEntriesFeed(), name='rss'),

    url(r'^search/', views.ProzdoSearchView.as_view(), name='search'),
    url(r'^autocomplete/$', views.ProzdoAutocompleteView.as_view(), name='autocomplete'),


]

urlpatterns.append(url(r'^(?P<alias>[a-z0-9_\-]{1,})/comment/(?P<comment_pk>\d+)/$', views.PostDetail.as_view(), kwargs={'action': 'comment'}, name='post-detail-alias-comment'))
urlpatterns.append(url(r'^(?P<alias>[a-z0-9_\-]{1,})/$', views.PostDetail.as_view(), kwargs={'action': 'normal'}, name='post-detail-alias'))
