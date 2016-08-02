from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponsePermanentRedirect, Http404
from django.views.generic import DetailView
from django.conf import settings

from .models import Page, get_or_create_struct_page


def page(request, *slugs):
    """
    Render page by it's alias (slugs list).
    Example: Suppose page "contacts" in DB have alias /navi/contacts/.
     - /articles/contacts/ alias should return 404
     - /contacts/ should return 301 redirect to /navi/contacts/
     - /navi/contacts/ should render "contacts" page
    """

    def render_page(request_, page_):
        return render(request_, 'pages/page.html', {
            'page': page_,
        })

    def path_exists(page_, slugs_path):
        """
        Return values example for "contacts" page with parent "navi":
         - /articles/contacts/ - false
         - /navi/contacts/ - true
        """
        return page_.get_path_as_slugs() == slugs_path

    page_ = get_object_or_404(Page, slug=slugs[-1])

    if len(slugs) == 1:
        # example: /contacts/ --301--> /navi/contacts/
        if page_.parent:
            return HttpResponsePermanentRedirect(page_.get_absolute_url())
    else:
        if not path_exists(page_, slugs):
            raise Http404('No pages matches to given query')

    return render_page(request, page_)


def robots(request):
    """Render robots.txt and send it as response"""
    return render_to_response(
        'robots.txt',
        {'debug': settings.DEBUG,
         'url': request.scheme + '://' + request.META['HTTP_HOST']},
        content_type='text/plain'
    )


class IndexPage(DetailView):
    model = Page
    template_name = 'index/index.html'
    context_object_name = 'page'

    def get_object(self, **kwargs):
        return get_or_create_struct_page(slug='index')
