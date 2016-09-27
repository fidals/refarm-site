from django import template
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage as storage


register = template.Library()


@register.simple_tag
def placeholder_image_url():
    """
    Use this image if you have image area, but have not actual image.
    In product card for product without image, for example.
    """
    try:
        return storage.url(settings.PLACEHOLDER_IMAGE)
    except FileNotFoundError as e:
        # TODO - some warn output: http://bit.ly/refarm-tail-enable-logging
        raise e
    except AttributeError as e:
        raise e
