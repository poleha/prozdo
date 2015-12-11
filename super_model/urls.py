from django.conf.urls import url
from . import views

urlpatterns = [
url(r'^history/ajax_save/$', views.HistoryAjaxSave.as_view(), name='history-ajax-save'),
        ]