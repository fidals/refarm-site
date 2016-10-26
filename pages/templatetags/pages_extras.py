from django import template
from django.core.urlresolvers import reverse

from pages.models import FlatPage, Page


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
    return reverse(Page.CUSTOM_PAGES_URL_NAME, args=args or ('', ))
