import math

from django.conf import settings
from django.http import HttpResponsePermanentRedirect, Http404
from django.shortcuts import render, get_object_or_404, render_to_response
from django.views.generic import DetailView, ListView
from django.views.generic.detail import SingleObjectMixin

from pages.models import CustomPage, FlatPage, Page


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


class SitemapPage(SingleObjectMixin, ListView):
    # `page_kwarg` is a text part of pagination hash in url
    page_kwarg = 'sitemap_page'
    paginate_by = 50
    paginator_max_links_per_page = 10
    slug_url_kwarg = 'page'
    template_name = 'pages/sitemap.html'
    queryset = Page.objects.order_by('name')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(SitemapPage, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        def prepare_page_range(paginator, current_page):
            max_links = self.paginator_max_links_per_page
            if len(paginator.page_range) > max_links:
                return range(current_page.number, current_page.number + max_links)
            else:
                return range(1, len(paginator.page_range))

        context = super(SitemapPage, self).get_context_data(**kwargs)
        paginator_links = prepare_page_range(context['paginator'], context['page_obj'])

        return {
            **context,
            'url_pagination_hash': self.page_kwarg,
            'paginator_pages': context['page_obj'],
            'paginator_links': paginator_links,
        }


def robots(request):
    return render_to_response(
        'robots.txt', {
            'debug': settings.DEBUG,
            # WE don't use request.scheme because of nginx proxy server and https on production
            'url': settings.BASE_URL
        }, content_type='text/plain')

