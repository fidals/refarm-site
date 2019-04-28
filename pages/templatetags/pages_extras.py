from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

from pages.models import CustomPage, FlatPage, Page

register = template.Library()


@register.inclusion_tag('pages/breadcrumbs.html')
def breadcrumbs(page: Page, separator=''):
    index = page.get_index()

    crumbs_list = (
        (index.display_menu_title, index.url) if index else ('Main', '/'),
        *page.get_ancestors_fields('display_menu_title', 'url', include_self=False),
        (page.display_menu_title, '')
    )

    return {
        'crumbs_list': crumbs_list,
        'separator': separator,
    }


@register.inclusion_tag('pages/breadcrumbs_with_siblings.html')
def breadcrumbs_with_siblings(page: Page, separator='', include_self=False):
    def get_siblings(page):
        def is_node(page):
           return hasattr(page.model, 'children')

        if not is_node(page):
            return []

        siblings = page.get_siblings().select_related(page.related_model_name)

        return [
            sibling
            for sibling in siblings
            if is_node(sibling)
        ]

    def get_ancestors_crumbs() -> list:
        ancestors_query = (
            page
            .select_related(page.related_model_name)
            .get_ancestors(include_self)
            .active()
        )

        if not ancestors_query.exists():
            return []

        catalog, *ancestors = ancestors_query

        siblings = [
            get_siblings(ancestor)
            for ancestor in ancestors
        ]

        return [
            (catalog.display_menu_title, catalog.url, []),
            *[
                (crumb.display_menu_title, crumb.url, crumb_links)
                for crumb, crumb_links in zip(ancestors, siblings)
            ],
        ]

    index = page.get_index()

    crumbs_list = [
        (index.display_menu_title, index.url, []) if index else ('Main', '/', []),
        *get_ancestors_crumbs(),
        (page.display_menu_title, '', get_siblings(page))
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
            FlatPage.objects.filter(type=Page.FLAT_TYPE)
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
    return reverse(CustomPage.ROUTE, args=args or ('',))


@register.simple_tag
def full_url(url_name, *args):
    return settings.BASE_URL + reverse(url_name, args=args)


@register.filter
def hasattr_(obj, arg):
    return hasattr(obj, arg)


@register.filter
def verbose_type(object):
    return object._meta.verbose_name.title()


@register.filter
def get_item(dictionary: dict, key: str):
    return dictionary.get(key)
