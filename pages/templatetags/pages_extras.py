from django import template

from pages.models import Page, get_or_create_struct_page

register = template.Library()


@register.inclusion_tag('pages/crumb.html')
def crumb(name, slug='/', separator='', position=0):
    return {
        'name': name,
        'slug': slug,
        'separator': separator,
        'position': position,
    }


@register.inclusion_tag('pages/breadcrumbs.html')
def breadcrumbs(page: Page, separator=''):

    def get_crumb(page_):
        return page_.menu_title, page_.get_absolute_url()

    index_page = get_or_create_struct_page(slug='index')
    crumbs_list = (
        [get_crumb(index_page)] +
        [get_crumb(p) for p in page.get_path(include_self=False)] +
        [(page.menu_title, '')]
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
            lambda p: p.is_section,
            Page.objects.all()
                .order_by(sort_field)
                .filter(is_active=True)
                .iterator()
        )
    )

    for section in sections:
        section.pages = \
            section.children.all().order_by(sort_field)[:links_per_item]

    return {
        'sections': sections,
    }
