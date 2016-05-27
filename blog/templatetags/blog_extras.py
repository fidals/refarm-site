from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

from blog.models import Post

register = template.Library()


@register.inclusion_tag('blog/accordion.html')
def accordion(links_per_item=10, sort_field='position'):
    """
    Renders posts accordion. Has post types as accordion items
    and posts as theirs nested items
    :param links_per_item: nested items count
    :param sort_field:
    """

    def get_sorted_items(type_: str, links_per_item_: int, sort_field_: str):
        return Post.objects.filter(type=type_).order_by(
            sort_field_, 'name')[:links_per_item_]

    def get_items_type_data(id_: str, type_: str,
                            links_per_item_: int, sort_field_: str) -> dict:
        return {
            'id': id_,
            'name': type_['name'],
            'slug': reverse('blog:posts', args=(id_,)),
            'items': get_sorted_items(id_, links_per_item_, sort_field_),
        }

    item_types = [get_items_type_data(id_, type_, links_per_item, sort_field)
                  for id_, type_ in settings.APP_BLOG_POST_TYPES.items()]
    return {
        'accordion_types': item_types,
        'posts_default_date': settings.SITE_CREATED,
    }
