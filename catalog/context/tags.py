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
        self._req_kwargs = req_kwargs

    def qs(self):
        raw_tags = self._kwargs.get('tags')
        if not raw_tags:
            self._tags.none()
        return self._tags.parsed(raw_tags)


class Checked404Tags(Tags):

    def __init__(self, tags: Tags):
        self._tags = tags

    def qs(self):
        tags = self._tags.qs()
        if not tags:
            raise http.Http404('No such tag.')
        return tags
