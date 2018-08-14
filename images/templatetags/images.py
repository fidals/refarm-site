from django import template
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage as storage


register = template.Library()


@register.simple_tag
def placeholder_image_url():
    """
    Use this image if you have image area, but have not actual image.
    In product card for product without image, for example.

    Architect thoughts:
    Question: Why this code in template tags, not in images.models?
    Answer: Placeholder has two key properties:
     - it's specific for particular site
     - it's used only for page rendering, not for data generation
    So, it's not in models module, but in template tags
    """
    try:
        return storage.url(settings.PLACEHOLDER_IMAGE)
    except FileNotFoundError as e:
        raise e
    except AttributeError as e:
        raise e
