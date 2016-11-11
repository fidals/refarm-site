from django.conf import settings

from pages.models import CustomPage, Page


def save_custom_pages():
    """
    This helper safely save custom pages data from settings.CUSTOM_PAGES to DB.
    It's useful in data migration scripts

    >>> settings.CUSTOM_PAGES = {'order': { 'slug': 'order', 'h1': 'Order page'}}
    >>> save_custom_pages()
    >>> custom_page = CustomPage.objects.get(slug='order')
    """
    for fields in settings.CUSTOM_PAGES.values():
        if 'type' not in fields:
            fields.update({'type': Page.CUSTOM_TYPE})
        page_in_db = bool(CustomPage.objects.filter(**fields))
        if not page_in_db:
            CustomPage.objects.create(**fields)
