from catalog.context.context import ModelContext
from catalog.models import AbstractProduct, Tag


class Tags(ModelContext):

    def __init__(self, qs):
        self._qs = qs

    def qs(self):
        return self._qs

    def context(self):
        return {
            'tags': self.qs(),
        }


class TagsByRaw(Tags):

    def __init__(self, qs, raw_tags: str):
        self._qs = qs
        self._raw_tags = raw_tags

    def qs(self):
        slugs = Tag.parse_url_tags(self._raw_tags)
        return self._qs.filter(slug__in=slugs)


class GroupTagsByProducts(Tags):

    def __init__(self, qs, products):
        self._qs = qs
        self._products = products

    def qs(self):
        return self._qs.filter_by_products(self._products)

    def context(self):
        return {
            **super().context(),
            'group_tags_pairs': self.qs().get_group_tags_pairs(),
        }


class Checked404Tags(Tags):

    def qs(self):
        tags = self.qs()
        if not tags:
            raise http.Http404('No such tag.')
        return tags
