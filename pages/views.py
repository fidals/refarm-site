from django.shortcuts import render, get_object_or_404
from django.http import HttpResponsePermanentRedirect, Http404

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

        return render_page(request, page_)

    if not path_exists(page_, slugs):
        raise Http404('No pages matches to given query')

    return render_page(request, page_)


def index(request):
    """Main page view: root categories, top products."""

    page_ = get_or_create_struct_page(slug='index')
    return render(request, 'pages/page.html', {'page': page_})
