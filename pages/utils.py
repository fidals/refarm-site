from django.conf import settings
from django.contrib.redirects.models import Site

from pages.models import CustomPage


def save_custom_pages():
    """
    This helper safely saves custom pages data from settings.CUSTOM_PAGES to DB.
    It's useful in data migration scripts

    >>> settings.CUSTOM_PAGES = {'order': { 'slug': 'order', 'h1': 'Order page'}}
    >>> save_custom_pages()
    >>> custom_page = CustomPage.objects.get(slug='order')
    """
    for fields in settings.CUSTOM_PAGES.values():
        page_in_db = CustomPage.objects.filter(**fields).exists()
        if not page_in_db:
            CustomPage.objects.create(**fields)


def init_redirects_app():
    site, _ = Site.objects.get_or_create(id=settings.SITE_ID)
    site.domain = settings.SITE_DOMAIN_NAME
    site.name = settings.SITE_DOMAIN_NAME
    site.save()