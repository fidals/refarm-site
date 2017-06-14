from search import views as search, search as search_engine

from tests.catalog.models import TestCategory, TestProduct


class TestSearch(search.SearchView):

    search_entities = [
        search_engine.Search(
            name='category',
            qs=TestCategory.objects.all(),
            fields=['name', 'id']
        ),
        search_engine.Search(
            name='product',
            qs=TestProduct.objects.all(),
            fields=['name', 'id']
        )
    ]
