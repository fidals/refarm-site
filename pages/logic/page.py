from pages import models


class Page:
    def __init__(self, model: models.Page):
        # "record" is much more good field name, i suppose.
        # But "model" is Django standard.
        self.model = model

    @property
    def siblings(self) -> models.PageQuerySet:
        return self.model.parent.children.exclude(id=self.model.id)

    @property
    def breadcrumbs(self) -> models.PageQuerySet:
        return (
            self.model
            .get_ancestors(include_self=True)
            .select_related(self.model.related_model_name)
            .active()
        )
