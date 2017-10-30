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


class MockAutocompleteView(search.AutocompleteView):
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

    entity_fields = {
        'category': ['name', 'url'],
        'product': ['name', 'price', 'url']
    }


class MockAdminAutocompleteView(search.AdminAutocompleteView):
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

    entity_fields = {
        'category': ['name', 'url'],
        'product': ['name', 'price', 'url']
    }
