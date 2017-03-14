from itertools import chain
from typing import List, Tuple

from django.core.urlresolvers import reverse_lazy
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render, _get_queryset
from django.views.generic import View

from catalog.models import AbstractCategory, AbstractProduct, search

from pages.views import CustomPageView
from pages.models import Page

SEARCH_RESULT = Tuple[List[AbstractCategory], List[AbstractProduct]]


class AbstractSearch(View):

    model_map = None
    search_limit = 20
    autocomplete_limit = 20
    lookups = ['name__icontains', 'id__contains']

    @property
    def category(self):
        assert self.model_map, 'model_map field should be defined'
        return self.model_map['category']

    @property
    def product(self):
        assert self.model_map, 'model_map field should be defined'
        return self.model_map['product']

    def search(self, term, limit, ordering=None):
        """Perform a search on models. Return evaluated QuerySet."""
        categories = search(term, self.category, self.lookups)[:limit]
        products = search(term, self.product, self.lookups, ordering)

        left_limit = limit - len(categories)
        products = products[:left_limit]

        return categories, products


class Search(CustomPageView, AbstractSearch):

    template_path = 'catalog/search/{}.html'

    def _search_product_by_id(self, term: str):
        return (
            _get_queryset(self.product).filter(id=term).first()
            if term.isdecimal() else None
        )

    def get(self, request, *args, **kwargs):
        term = request.GET.get('term')

        # 404 - the most convenient error for bad get param
        # http://bit.ly/refarm_conv_404_on_wrong_get_param
        if not term:
            raise Http404('Define "term" get parameter')

        # if we have product with id == int(term)
        # then redirect to this product
        product = self._search_product_by_id(term)
        if product:
            return redirect(product.url, permanent=True)

        categories, products = self.search(term, self.search_limit)

        # if there is only one autocompleted entity
        # then redirect to this entity
        merged_queryset = list(chain(categories, products))
        if len(merged_queryset) == 1:
            return redirect(merged_queryset[0].url, permanent=True)

        self.object = self.get_object()
        template = self.template_path.format(
            'results' if categories or products else 'no_results')

        context = self.get_context_data(object=self.object)
        context.update({
            'categories': categories,
            'products': products,
            'term': term
        })

        return render(request, template, context)


class Autocomplete(AbstractSearch):

    search_url = reverse_lazy(Page.CUSTOM_PAGES_URL_NAME, kwargs={'page': 'search'})
    see_all_label = 'See all results'

    # Default ordering fields
    default_ordering_fields = ('name', )

    # Used for client's code for extending fields to search
    extra_ordering_fields = ()

    # Default entities' fields for search
    default_entity_fields = {
        'product': {
            'name',
            'price',
            'url',
        },
        'category': {
            'name',
            'url',
        }
    }

    # Used for client's code for extending fields to search
    extra_entity_fields = {}

    def prepare_fields(self, items, entity, context) -> list:
        def get_dict(item):
            fields = {attr: getattr(item, attr) for attr in entity}
            fields.update(context)
            return fields

        return [get_dict(item) for item in items]

    def see_all_link_as_list(self, term):
        url = '{}?term={}'.format(self.search_url, term)
        return [{'name': self.see_all_label,
                 'url': url,
                 'type': 'see_all'}]

    def get_result_entity_fields(self):
        result_entity_fields = self.default_entity_fields.copy()

        for key in result_entity_fields:
            if key in self.extra_entity_fields:
                result_entity_fields[key].update(self.extra_entity_fields[key])

        return result_entity_fields

    def get_result_ordering_fields(self):
        return self.default_ordering_fields + self.extra_ordering_fields

    def get(self, request):
        term = request.GET.get('term')
        entity_fields = self.get_result_entity_fields()
        ordering_fields = self.get_result_ordering_fields()
        categories, products = self.search(
            term=term,
            limit=self.autocomplete_limit,
            ordering=ordering_fields
        )

        if not categories and not products:
            return JsonResponse({})

        autocomplete_items = (
            self.prepare_fields(categories, entity_fields['category'], {'type': 'category'}) +
            self.prepare_fields(products, entity_fields['product'], {'type': 'product'}) +
            self.see_all_link_as_list(request.GET.get('term'))
        )

        return JsonResponse(autocomplete_items, safe=False)


class AdminAutocomplete(AbstractSearch):

    def get(self, request):
        term, page_type = request.GET.get('term'), request.GET.get('pageType')
        if page_type not in self.model_map:
            return

        current_model = self.model_map[page_type]

        autocomplete_items = search(term, current_model, self.lookups)[:self.autocomplete_limit]
        names = [item.name for item in autocomplete_items]

        return JsonResponse(names, safe=False)
