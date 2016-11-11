from django.conf.urls import url, include

from pages import views
from pages.models import Page

app_name = 'pages'

urlpatterns = [
    url(r'^', include('pages.urls')),
    url(r'^(?P<page>)$', views.CustomPageView.as_view(), name=Page.CUSTOM_PAGES_URL_NAME),
]
