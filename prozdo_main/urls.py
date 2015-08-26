from django.conf.urls import url
from . import views
#from django.views.decorators.cache import cache_page

urlpatterns = [
    #url(r'^drug/detail/(?P<pk>\d+)$', views.DrugDetail.as_view(), name='drug-detail'),
    url(r'^drug/list', views.DrugList.as_view(), name='drug-list'),
    url(r'^(?P<alias>[a-z0-9_]{1,})$', views.PostDetail.as_view(), name='post-detail'),

    url(r'^drug/detail/(?P<pk>\d+)$', views.PostDetail.as_view(), kwargs={'klass': 'Drug'}, name='drug-detail'),

]
