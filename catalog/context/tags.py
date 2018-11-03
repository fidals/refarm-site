from catalog.context.context import Context, Tags, Products

from django.db.models import QuerySet


class GroupedTags(Context):

    def __init__(self, tags: Tags):
        self._tags = tags

    def context(self):
        return {
            'group_tags_pairs': self._tags.qs().get_group_tags_pairs(),
        }


class ParsedTags(Tags):

    def __init__(self, tags: Tags, req_kwargs):
        self._tags = tags
        self._raw_tags = req_kwargs.get('tags')

    def qs(self):
        tags = self._tags.qs()
        if not self._raw_tags:
            tags.none()
        return tags.parsed(self._raw_tags)


class Checked404Tags(Tags):

    def __init__(self, tags: Tags):
        self._tags = tags

    def qs(self):
        tags = self._tags.qs()
        if not tags.exists():
            raise http.Http404('No such tag.')
        return tags
