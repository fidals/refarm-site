from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponsePermanentRedirect, Http404
from django.views.generic import DetailView
from django.conf import settings

from pages.models import Page, get_or_create_struct_page


class CustomPage(DetailView):
    """
    Class based views for page.
    Render custom page by it's slug.
    """
    model = Page
    template_name = 'pages/page.html'
    context_object_name = 'page'
    slug_field = 'index'
    context = {}

    def get_object(self, *args):
        """If entity exist - fetch it, else 404"""
        return get_object_or_404(self.model, slug=args[0])

    def get(self, request, *args, **kwargs):
        """Get method for page"""
        page = self.get_object(args or self.slug_field)
        context = {
            self.context_object_name: page,
            **self.context
        }
        return render(request, self.template_name, context)


class FlatPage(CustomPage):
    """
    Class based views for flat page.
    Render page by it's alias (slugs list).
    Example: Suppose page "contacts" in DB have alias /navi/contacts/.
     - /articles/contacts/ alias should return 404
     - /contacts/ should return 301 redirect to /navi/contacts/
     - /navi/contacts/ should render "contacts" page
    """
    __entity_page = None

    def is_full_path(self, page, slugs):
        """Check URI path, if is not full - 301 to actual URI"""
        if len(slugs) == 1 and page.parent:
            return HttpResponsePermanentRedirect(page.get_absolute_url())

    def is_path_exist(self, page, slugs_path):
        """Check URI path, if is not exist - raise 404"""
        if page.get_path_as_slugs() != slugs_path:
            raise Http404('No pages matches to given query')

    validation_methods = [is_full_path, is_path_exist]

    def get_object(self, slugs_path):
        """If entity exist - fetch it, else 404"""
        return self.__entity_page or get_object_or_404(self.model, slug=slugs_path[-1])


    def get(self, request, *args):
        """Get method for flat page"""
        page = self.__entity_page = self.get_object(args)
        for method in self.validation_methods or []:
            method_response = method(self, page, args)
            if method_response:
                return method_response
        return super(FlatPage, self).get(request, args)

# TODO needed remove it
class IndexPage(DetailView):
    model = Page
    template_name = 'index/index.html'
    context_object_name = 'page'

    def get_object(self, **kwargs):
        return get_or_create_struct_page(slug='index')


def robots(request):
    """Render robots.txt and send it as response"""
    return render_to_response(
        'robots.txt',
        {'debug': settings.DEBUG,
         'url': request.scheme + '://' + request.META['HTTP_HOST']},
        content_type='text/plain'
    )
