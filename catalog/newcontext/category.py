from catalog.models import AbstractCategory
from pages.newcontext import Context as BaseContext


class Context(BaseContext):
    def __init__(self, category: AbstractCategory):
        self.category = category

    def context(self):
        return {
            'category': self.category,
            'children': self.category.get_children(),
        }
