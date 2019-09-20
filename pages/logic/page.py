import typing

from pages import models


class Page:
    def __init__(self, model: models.Page):
        # "record" is much more good field name, i suppose.
        # But "model" is Django standard.
        self.model = model

    def __str__(self):
        return f'<logic.Page: {str(self.model)}>'

    @property
    def siblings(self) -> models.PageQuerySet:
        return self.model.parent.children.exclude(id=self.model.id)

    @property
    def breadcrumbs(self) -> 'Pages':
        return Pages(
            self.model
            .get_ancestors(include_self=True)
            .select_related(self.model.related_model_name)
            .active()
        )


class Pages:
    def __init__(self, models: typing.Iterable[models.Page]):
        self.models = models

    def __iter__(self):
        for model in self.models:
            yield Page(model)
