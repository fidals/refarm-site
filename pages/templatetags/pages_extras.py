from itertools import groupby

from django import template
from django.core.urlresolvers import reverse

from pages.models import FlatPage, ModelPage, Page

register = template.Library()


@register.inclusion_tag('pages/breadcrumbs.html')
def breadcrumbs(page: Page, separator=''):
    index = page.get_index()

    crumbs_list = (
        (index.menu_title, index.url) if index else ('Main', '/'),
        *page.get_ancestors_fields('menu_title', 'url', include_self=False),
        (page.menu_title, '')
    )

    return {
        'crumbs_list': crumbs_list,
        'separator': separator,
    }


@register.inclusion_tag('pages/breadcrumbs_with_siblings.html')
def breadcrumbs_with_siblings(page: Page, separator='', include_self=False):
    def get_ancestors_crumbs() -> list:
        related_model_names = [
            page.related_model_name
            for page in ModelPage.objects.distinct('related_model_name')
        ]

        ancestors_query = page.get_ancestors(include_self).select_related(*related_model_names)

        if not ancestors_query.exists():
            return []

        catalog, *ancestors = (
            page
                .get_ancestors(include_self)
                .select_related(*related_model_names)
        )

        siblings = [
            ancestor
                .get_siblings()
                .select_related(*related_model_names)
            for ancestor in ancestors
        ]

        return [
            (catalog.menu_title, catalog.url, tuple()),
            *tuple(
                (current_crumb.menu_title, current_crumb.url, current_crumb_links)
                for current_crumb, current_crumb_links in zip(ancestors, siblings)
            ),
        ]

    index = page.get_index()

    crumbs_list = [
        (index.menu_title, index.url, tuple()) if index else ('Main', '/', tuple()),
        *get_ancestors_crumbs(),
        (page.menu_title, '', tuple())
    ]

    return {
        'index_slug': index.url if index else '/',
        'crumbs_list': crumbs_list,
        'separator': separator,
    }


@register.inclusion_tag('pages/accordion.html')
def accordion(links_per_item=10, sort_field='position'):
    """Render accordion with root pages as main items"""

    # root pages list
    sections = list(
        filter(
            lambda p: p.is_root,
            FlatPage.objects.all()
                .order_by(sort_field)
                .filter(is_active=True)
                .iterator()
        )
    )

    for section in sections:
        section.pages = section.children.all().order_by(sort_field)[:links_per_item]

    return {
        'sections': sections,
    }


@register.simple_tag
def custom_url(*args):
    return reverse(Page.CUSTOM_PAGES_URL_NAME, args=args or ('',))
