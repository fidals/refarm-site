from django.conf.urls import url, include
from django.conf import settings

from pages import views

app_name = 'pages'

urlpatterns = [
    url(r'^', include('pages.urls')),
    url(r'^(?P<page>)$', views.CustomPageView.as_view(), name=settings.CUSTOM_PAGES_URL_NAME),
]
