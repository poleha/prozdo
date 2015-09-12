from django.conf.urls import url
from . import views
#from django.views.decorators.cache import cache_page

urlpatterns = [
    #url(r'^drug/detail/(?P<pk>\d+)$', views.DrugDetail.as_view(), name='drug-detail'),
    url(r'^drug/list$', views.PostList.as_view(), name='drug-list', kwargs={'post_type': 'drug'}),
    url(r'^drug/list/letter/(?P<letter>[a-zа-я0-9])$', views.PostList.as_view(), kwargs={'action': 'alphabet', 'post_type': 'drug'}, name='drug-list-letter'),
    url(r'^drug/create$', views.PostCreate.as_view(), name='drug-create', kwargs={'post_type': 'drug'}),
    url(r'^drug/update/(?P<pk>\d+)$', views.PostUpdate.as_view(), name='drug-update', kwargs={'post_type': 'drug'}),

    url(r'^cosmetics/list$', views.PostList.as_view(), name='cosmetics-list', kwargs={'post_type': 'cosmetics'}),
    url(r'^cosmetics/list/letter/(?P<letter>[a-zа-я0-9])$', views.PostList.as_view(), kwargs={'action': 'alphabet', 'post_type': 'cosmetics'}, name='cosmetics-list-letter'),
    url(r'^cosmetics/create$', views.PostCreate.as_view(), name='cosmetics-create', kwargs={'post_type': 'cosmetics'}),
    url(r'^cosmetics/update/(?P<pk>\d+)$', views.PostUpdate.as_view(), name='cosmetics-update', kwargs={'post_type': 'cosmetics'}),

    url(r'^blog/list$', views.PostList.as_view(), name='blog-list', kwargs={'post_type': 'blog'}),
    url(r'^blog/create$', views.PostCreate.as_view(), name='blog-create', kwargs={'post_type': 'blog'}),
    url(r'^blog/update/(?P<pk>\d+)$', views.PostUpdate.as_view(), name='blog-update', kwargs={'post_type': 'blog'}),

    url(r'^component/list$', views.PostList.as_view(), name='component-list', kwargs={'post_type': 'component'}),
    url(r'^component/list/letter/(?P<letter>[a-zа-я0-9])$', views.PostList.as_view(), kwargs={'action': 'alphabet', 'post_type': 'component'}, name='component-list-letter'),
    url(r'^component/create$', views.PostCreate.as_view(), name='component-create', kwargs={'post_type': 'component'}),
    url(r'^component/update/(?P<pk>\d+)$', views.PostUpdate.as_view(), name='component-update', kwargs={'post_type': 'component'}),

    url(r'^post/(?P<pk>\d+)$', views.PostDetail.as_view(), kwargs={'action': 'normal'}, name='post-detail-pk'),
    url(r'^post/(?P<pk>\d+)/comment/(?P<comment_pk>\d+)$', views.PostDetail.as_view(), kwargs={'action': 'comment'}, name='post-detail-pk-comment'),

    url(r'^history/ajax_save$', views.HistoryAjaxSave.as_view(), name='history-ajax-save'),

    url(r'^comment/get_tree_ajax$', views.CommentGetTreeAjax.as_view(), name='get-comment-tree-ajax'),



    url(r'^comment/get_tiny_ajax$', views.CommentGetTinyAjax.as_view(), name='comment-get-tiny-ajax'),

    url(r'^comment/get_for_answer_block_ajax$', views.CommentGetForAnswerToBlockAjax.as_view(), name='comment-get-for-answer-block-ajax'),

    url(r'^comment/show_marked_users_ajax$', views.CommentShowMarkedUsersAjax.as_view(), name='comment-show-marked-users-ajax'),

    url(r'^signup$', views.ProzdoSignupView.as_view(), name='signup'),
    url(r'^login$', views.ProzdoLoginView.as_view(), name='login'),
    url(r'^logout$', views.ProzdoLogoutView.as_view(), name='logout'),
    url(r'^password_change$', views.ProzdoPasswordChangeView.as_view(), name='password-change'),
    url(r'^password_reset$', views.ProzdoPasswordResetView.as_view(), name='password-reset'),
    url(r'^password_reset_done$', views.ProzdoPasswordResetDoneView.as_view(), name='password-reset-done'),
    url(r"^password_reset_from_key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        views.ProzdoPasswordResetFromKeyView.as_view(),
        name="password-reset-from-key"),
    url(r"^password_reset_from_key_done/$", views.ProzdoPasswordResetFromKeyDoneView.as_view(),
        name="password-reset-from-key-done"),

    url(r'^user_profile$', views.UserProfileView.as_view(), name='user-profile'),
    url(r'^user/(?P<pk>\d+)$', views.UserDetailView.as_view(), name='user-detail'),
    url(r'^user/comments/(?P<pk>\d+)$', views.UserCommentsView.as_view(), name='user-comments'),
    url(r'^user/karma/(?P<pk>\d+)$', views.UserKarmaView.as_view(), name='user-karma'),

    url(r'^$', views.MainPageView.as_view(), name='main-page'),

]

urlpatterns.append(url(r'^(?P<alias>[a-z0-9_./]{1,})$', views.PostDetail.as_view(), kwargs={'action': 'normal'}, name='post-detail-alias'))
urlpatterns.append(url(r'^(?P<alias>[a-z0-9_./]{1,})/comment/(?P<comment_pk>\d+)$', views.PostDetail.as_view(), kwargs={'action': 'comment'}, name='post-detail-alias-comment'))