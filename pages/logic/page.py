import typing

from pages import models


class Page:
    def __init__(self, model: models.Page):
        # "record" is much more good field name, i suppose.
        # But "model" is Django standard.
        self.model = model

    def breadcrumbs(self) -> 'Breadcrumbs':
        pass

    @property
    def siblings(self) -> models.PageQuerySet:
        return self.model.parent.children.exclude(id=self.model.id)


# @todo #343:60m  Implement Breadcrumbs class.
#  Use it instead of monolithic logic at the `breadcrumbs_with_siblings`.
#  Create Breadcrumb class or named tuple to specify crumb data structure.
class Breadcrumbs:
    def __init__(self, page_model: models.Page):
        self.model = page_model

    def query(self, include_self: bool) -> models.PageQuerySet:
        return (
            self.model
            .get_ancestors(include_self)
            .select_related(self.model.related_model_name)
            .active()
        )

    def list(self, include_self=False) -> typing.List[typing.Tuple[str, str]]:
        """Breadcrumbs list consists of current page ancestors."""
        return [
            (crumb.display_menu_title, crumb.url)
            for crumb in self.query(include_self).iterator()
        ]

    def list_with_self(self) -> list:
        return self.list(include_self=True)

