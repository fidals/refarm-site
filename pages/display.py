"""
Views processing db based templates.
This view are outside of MTV concept.
Responsible only for rendering given context data with db preserved text template.
"""
import typing

from collections import defaultdict


class Page:
    """It's python Descriptor."""

    # @todo #240:30m  Create usage doc for page view.

    # Fields stored in DB. See class `pages.models.PageTemplate`
    STORED = ['name', 'h1', 'keywords', 'description', 'title', 'seo_text']

    def __init__(self, page: 'pages.models.Page'=None, context: typing.Dict[str, typing.Any]=None):
        """
        Pass context at ctor, but not render method,
        because client code wants the same context for many different cases.
        """
        self._page = page
        self._global_context = defaultdict(dict)
        if context:
            self._global_context[page.id] = context

    def __get__(self, instance: 'pages.models.Page', type_):
        return Page(
            instance,
            {'page': instance, **self._global_context[instance.id]}
        )

    def __set__(self, instance: 'pages.models.Page', value: typing.Dict[str, typing.Any]):
        self._page = instance
        self._global_context[instance.id] = value

    def __getattr__(self, item):
        if item in self.STORED:
            return self.render(item)
        else:
            return super().__getattribute__(item)

    def render(self, field: str):
        return (
            self._page.template.render_field(
                field, context=self._global_context[self._page.id]
            )
            if self._page.template
            else getattr(self._page, field)
        )
