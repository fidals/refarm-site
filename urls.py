from django.conf.urls import url
from . import views

app_name = 'blog'
urlpatterns = [
    url(r'^$', views.pages_list, name='pages_list'),
    url(r'^(?P<page_id>[0-9]+)/$', views.page_item, name='page'),
]
