from typing import List, Tuple

from django.core.urlresolvers import reverse_lazy
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import View

from catalog.models import AbstractCategory, AbstractProduct
from search import search as search_engine

from pages.views import CustomPageView
from pages.models import Page

SEARCH_RESULT = Tuple[List[AbstractCategory], List[AbstractProduct]]


class SearchView(CustomPageView):

    limit = 20
    template_path = 'search/{}.html'
    search_entities = []
    redirect_search_entity = None

    def get(self, request, *args, **kwargs):
        term = request.GET.get('term')

        # 404 - the most convenient error for bad get param
        # http://bit.ly/refarm_conv_404_on_wrong_get_param
        if not term:
            raise Http404('Define "term" get parameter')

        # if we have entity with id == int(term)
        # then redirect to this entity
        if self.redirect_search_entity is not None:
            search_entity = self.redirect_search_entity.search_by_redirect_field(term)
            if search_entity:
                return redirect(search_entity.url, permanent=True)

        search_limit = search_engine.Limit(self.limit)
        search_result = {
            entity.name: search_limit.limit_data(entity.search(term))
            for entity in self.search_entities
        }

        # if there is only one autocompleted entity
        # then redirect to this entity
        if search_limit.size == 1:
            return redirect(list(search_result.values())[0][0].url, permanent=True)

        self.object = self.get_object()
        template = self.template_path.format(
            'results' if search_result else 'no_results')

        context = self.get_context_data(object=self.object)
        context.update({
            **search_result,
            'term': term
        })

        return render(request, template, context)


class Autocomplete(View):

    limit = 20
    search_entities = []  # query lookups
    entity_fields = {}  # model fields that will be contained in the autocomplete item

    search_url = reverse_lazy(Page.CUSTOM_PAGES_URL_NAME, kwargs={'page': 'search'})
    see_all_label = 'See all results'

    @staticmethod
    def prepare_fields(items, entity, context) -> list:
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

    def get(self, request):
        term = request.GET.get('term')

        search_limit = search_engine.Limit(self.limit)
        search_result = {
            entity.name: search_limit.limit_data(entity.search(term))
            for entity in self.search_entities
        }

        if not search_result:
            return JsonResponse({})

        autocomplete_items = (
            self.prepare_fields(
                search_result.get('category', []),
                self.entity_fields['category'],
                {'type': 'category'}
            ) +
            self.prepare_fields(
                search_result.get('product', []),
                self.entity_fields['product'],
                {'type': 'product'}
            ) +
            self.see_all_link_as_list(request.GET.get('term'))
        )

        return JsonResponse(autocomplete_items, safe=False)


class AdminAutocomplete(View):

    limit = 20
    search_entities = []

    def get(self, request):
        term, page_type = request.GET.get('term'), request.GET.get('pageType')

        current_search = next(
            (item for item in self.search_entities if item.name == page_type),
            None
        )
        if not current_search:
            return

        current_model = next(
            (item for item in self.search_entities if item.name == page_type),
            None
        )

        search_limit = search_engine.Limit(self.limit)
        search_result = {
            current_model.name: search_limit.limit_data(current_model.search(term))
        }

        names = [result_item.name for result_item in search_result[current_model.name]]
        return JsonResponse(names, safe=False)
