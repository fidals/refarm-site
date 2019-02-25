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

    def __init__(
        self,
        context: typing.Dict[str, typing.Any]=None,
        *,
        _page: 'pages.models.Page'=None,
        _name='',
    ):
        """
        Pass context at ctor, but not render method,
        because client code wants the same context for many different cases.
        """
        self._context = context or {}
        self._page = _page
        self._name = _name

    def __set_name__(self, instance, name):
        # get `Page` instace to create new `Page` instance with `name`
        page = getattr(instance, name)
        page_with_name = Page(page._context, _page=page._page, _name=name)
        # Set new `Page` instance with name
        setattr(instance, name, page_with_name)

    def __get__(self, instance: 'pages.models.Page', type_):
        if instance and self._name in instance.__dict__:
            return instance.__dict__[self._name]
        return Page(
            {'page': instance, **self._context},
            _page=instance,
            _name=self._name,
        )

    def __set__(self, instance: 'pages.models.Page', value: typing.Dict[str, typing.Any]):
        if not isinstance(value, dict):
            raise ValueError(f'Value should be a dict')

        if self._name in instance.__dict__:
            # merge old context with new one
            context = {**instance.__dict__[self._name]._context, **value}
        else:
            context = {**self._context, **value}

        instance.__dict__[self._name] = Page(context, _page=instance, _name=self._name)

    def __getattr__(self, item):
        if item in self.STORED:
            return self.render(item)
        else:
            return super().__getattribute__(item)

    def render(self, field: str):
        return (
            self._page.template.render_field(field, context=self._context)
            if self._page.template
            else getattr(self._page, field)
        )
