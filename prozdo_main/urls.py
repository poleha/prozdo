from django.conf.urls import url
from . import views
#from django.views.decorators.cache import cache_page

urlpatterns = [
    #url(r'^drug/detail/(?P<pk>\d+)$', views.DrugDetail.as_view(), name='drug-detail'),
    url(r'^drug/list', views.DrugList.as_view(), name='drug-list'),

    url(r'^post/detail/(?P<pk>\d+)$', views.PostDetail.as_view(), name='post-detail-pk'),

    url(r'^history/ajax_save', views.HistoryAjaxSave.as_view(), name='history-ajax-save'),

    url(r'^comment/get_tree_ajax', views.CommentGetTreeAjax.as_view(), name='get-comment-tree-ajax'),

    url(r'^comment/get_tiny_ajax', views.CommentGetTinyAjax.as_view(), name='comment-get-tiny-ajax'),

    url(r'^comment/get_tiny_ajax', views.CommentGetTinyAjax.as_view(), name='comment-get-tiny-ajax'),

    url(r'^comment/show_marked_users_ajax', views.CommentShowMarkedUsersAjax.as_view(), name='comment-show-marked-users-ajax'),

    url(r'^signup', views.ProzdoSignupView.as_view(), name='signup'),
    url(r'^login', views.ProzdoLoginView.as_view(), name='login'),

    url(r'^$', views.MainPageView.as_view(), name='main-page'),

]

urlpatterns.append(url(r'^(?P<alias>[a-z0-9_]{1,})$', views.PostDetail.as_view(), kwargs={'action': 'normal'}, name='post-detail-alias'))
urlpatterns.append(url(r'^(?P<alias>[a-z0-9_]{1,})/comment/(?P<pk>\d+)$', views.PostDetail.as_view(), kwargs={'action': 'comment'}, name='post-detail-alias-comment'))