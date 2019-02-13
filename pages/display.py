"""
Views processing db based templates.
This view are outside of MTV concept.
Responsible only for rendering given context data with db preserved text template.
"""
import typing

from pages import models


class Fields:
    # Fields stored in DB. See class `pages.models.PageTemplate`
    STORED = ['name', 'h1', 'keywords', 'description', 'title', 'seo_text']

    def __init__(self, page_display: 'Page'):
        self.page_display = page_display

    def __getattr__(self, item):
        if item in self.STORED:
            return self.page_display.render(item)
        else:
            return super().__getattribute__(item)


class Page:
    # @todo #240:30m  Create usage doc for page view.

    def __init__(self, page: models.Page, context: typing.Dict[str, typing.Any]):
        """
        Pass context at ctor, but not render method,
        because client code wants the same context for many different cases.
        """
        self.page = page
        self.context = context
        self.fields = Fields(self)

    def render(self, field: str):
        return (
            self.page.template.render_field(field, self.context)
            if self.page.template
            else getattr(self.page, field)
        )
