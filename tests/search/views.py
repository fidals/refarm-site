from search import views as search, search as search_engine

from tests.catalog.models import MockCategory, MockProduct


class MockSearchView(search.SearchView):

    search_entities = [
        search_engine.Search(
            name='category',
            qs=MockCategory.objects.all(),
            fields=['name', 'id']
        ),
        search_engine.Search(
            name='product',
            qs=MockProduct.objects.all(),
            fields=['name', 'id']
        )
    ]
