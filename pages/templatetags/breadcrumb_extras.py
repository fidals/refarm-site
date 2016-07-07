from django import template

register = template.Library()


@register.inclusion_tag('seo/crumb.html')
def crumb(name, alias='/', separator=''):
    return {
        'name': name,
        'alias': alias,
        'separator': separator,
    }


@register.inclusion_tag('seo/breadcrumbs.html')
def breadcrumbs(crumbs_list, separator=''):
    return {
        'crumbs_list': crumbs_list,
        'separator': separator,
    }
