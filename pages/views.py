from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponsePermanentRedirect, Http404
from django.views.generic import DetailView
from django.conf import settings

from pages.models import CustomPage, FlatPage


class CustomPageView(DetailView):
    """
    Class based views for page.
    Render custom page by it's slug.
    """
    model = CustomPage
    template_name = 'index/index.html'
    slug_url_kwarg = 'page'
    context_object_name = 'page'


class FlatPageView(DetailView):
    """
    Class based views for flat page.
    Render page by it's alias (slugs list).
    Example: Suppose page "contacts" in DB have alias /navi/contacts/.
     - /articles/contacts/ alias should return 404
     - /contacts/ should return 301 redirect to /navi/contacts/
     - /navi/contacts/ should render "contacts" page
    """
    model = FlatPage
    template_name = 'pages/page.html'
    context_object_name = 'page'

    def is_full_path(self, request, page):
        """
        (ex. suppose, we have entity 'contacts' with path /navi/contacts/
        if path=/contacts/ return False
        if path=/navi/contacts/ return True)
        """
        return request.path == page.url

    def is_correct_path(self, slugs, page):
        """
        (ex. suppose, we have entity 'contacts' with path /navi/contacts/
        if path=/navi/contacts/ return True)
        if path=/job/contacts/ return False
        """
        return '/'.join(slugs) in page.url

    def get(self, request, *args):
        """Get method for flat page"""
        self.object = page = get_object_or_404(self.model, slug=args[-1])

        if not self.is_correct_path(args, page):
            """Check URL path, if is not correct - 404"""
            raise Http404()

        if not self.is_full_path(request, page):
            """Check URL path, if is not full - 301 to actual URL"""
            return HttpResponsePermanentRedirect(page.url)

        context = self.get_context_data(object=page)
        return render(request, self.template_name, context)


def robots(request):
    return render_to_response(
        'robots.txt', {
            'debug': settings.DEBUG,
            # WE don't use request.scheme because of nginx proxy server and https on production
            'url': settings.BASE_URL
        }, content_type='text/plain')
