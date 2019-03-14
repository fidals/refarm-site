from catalog import typing

from .context import Context
from .tags import Tags


class Page(Context):

    def __init__(self, page, tags: Tags):
        self._page = page
        self._tags = tags

    def context(self) -> typing.ContextDict:
        tags_qs = self._tags.qs()
        # use dirty patch here, because it's the most simple method
        # to make shared templates work.
        # For example `templates/layout/metadata.html`.
        self._page.display = {
            'page': self._page,
            'tag_titles': tags_qs.as_title(),
            'tags': tags_qs,
        }
        return {
            'page': self._page,
        }
