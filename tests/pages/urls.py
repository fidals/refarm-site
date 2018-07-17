from django.conf.urls import url, include

from pages import views
from pages.urls import custom_page_url

urlpatterns = [
    url(r'^', include('pages.urls')),
    custom_page_url(r'^(?P<page>)$', views.CustomPageView.as_view()),
    custom_page_url(r'^(?P<page>robots)$', views.RobotsView.as_view()),
    custom_page_url(r'^(?P<page>robots-404)$', views.RobotsView.as_view()),
]
