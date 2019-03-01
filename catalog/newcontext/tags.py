from django.http import Http404

from catalog import models
from catalog.newcontext.context import Context, Tags


class TagsByProducts(Tags):

    def __init__(self, tags: Tags, products: models.ProductQuerySet):
        self._tags = tags
        self.products = products

    def qs(self):
        return self._tags.qs().filter_by_products(self.products)


class GroupedTags(Context):

    def __init__(self, tags: Tags):
        self._tags = tags

    def context(self):
        return {
            'group_tags_pairs': self._tags.qs().group_tags().items(),
        }


class ParsedTags(Tags):

    def __init__(self, tags: Tags, raw_tags=''):
        self._tags = tags
        self._raw_tags = raw_tags

    def qs(self):
        tags = self._tags.qs()
        if not self._raw_tags:
            return tags.none()
        return tags.parsed(self._raw_tags)


class Checked404Tags(Tags):

    def __init__(self, tags: Tags):
        self._tags = tags

    def qs(self):
        tags = self._tags.qs()
        if not tags.exists():
            raise Http404('No such tag.')
        return tags
