from django.conf.urls import url, include

urlpatterns = [
    url(r'^pages/', include('blog.urls')),
]
