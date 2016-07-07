from django.conf.urls import url, include
from pages import views

urlpatterns = [
    url(r'^', include('pages.urls')),
    url(r'^$', views.index, name='index'),
]
