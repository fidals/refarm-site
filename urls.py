from django.conf.urls import url, include

from . import views

app_name = "blog"
urlpatterns = [
    url(r'^$', views.pages_list, name="list"),
    url(r'^item/(?P<page_id>[0-9]+)/$', views.page_item, name="page"),
]
