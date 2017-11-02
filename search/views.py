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

    def get_redirect_search_entity(self):
        pass

    def get(self, request, *args, **kwargs):
        term = request.GET.get('term')

        # 404 - the most convenient error for bad get param
        # http://bit.ly/refarm_conv_404_on_wrong_get_param
        if not term:
            raise Http404('Define "term" get parameter')

        # if we have entity with id == int(term)
        # then redirect to this entity
        redirect_search_entity = self.get_redirect_search_entity()
        if redirect_search_entity:
            search_entity = redirect_search_entity.search_by_redirect_field(term)
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
            for results_qs in search_result.values():
                if results_qs:
                    return redirect(
                        to=results_qs[0].url,
                        permanent=True
                    )

        has_result = any(search_result.values())
        self.object = self.get_object()
        template = self.template_path.format(
            'results' if has_result else 'no_results'
        )

        context = self.get_context_data(object=self.object)
        context.update({
            **search_result,
            'term': term
        })

        return render(request, template, context)


class AutocompleteView(View):

    limit = 20
    search_entities = []  # query lookups

    search_url = reverse_lazy(Page.CUSTOM_PAGES_URL_NAME, kwargs={'page': 'search'})
    see_all_label = 'See all results'

    @staticmethod
    def prepare_fields(items, fields, context) -> list:
        def get_dict(item):
            # pairs of {name: value}
            field_pairs = {attr: getattr(item, attr) for attr in fields}
            field_pairs.update(context)
            return field_pairs

        return [get_dict(item) for item in items]

    def see_all_link_as_list(self, term):
        url = '{}?term={}'.format(self.search_url, term)
        return [{'name': self.see_all_label,
                 'url': url,
                 'type': 'see_all'}]

    def get(self, request):
        def get_search_fields(search_name: str) -> List[str]:
            """
            Return search fields for Search instance with name `search_name`
            :param search_name:
            :return:
            """
            search = next(
                s for s in self.search_entities if s.name == search_name
            )
            return search.template_fields

        term = request.GET.get('term')

        # 404 - the most convenient error for bad get param
        # http://bit.ly/refarm_conv_404_on_wrong_get_param
        if not term:
            raise Http404('Define "term" get parameter')

        search_limit = search_engine.Limit(self.limit)
        search_result = {
            entity.name: search_limit.limit_data(entity.search(term))
            for entity in self.search_entities
        }

        if not any(search_result.values()):
            return JsonResponse({})

        autocomplete_items = (
            self.prepare_fields(
                search_result.get('category', []),
                get_search_fields('category'),
                {'type': 'category'}
            ) +
            self.prepare_fields(
                search_result.get('product', []),
                get_search_fields('product'),
                {'type': 'product'}
            ) +
            self.see_all_link_as_list(request.GET.get('term'))
        )

        return JsonResponse(autocomplete_items, safe=False)


class AdminAutocompleteView(View):

    limit = 20
    search_entities = []

    def get(self, request):
        term, page_type = request.GET.get('term'), request.GET.get('pageType')

        search_expression = next(
            (item for item in self.search_entities if item.name == page_type),
            None
        )
        if not search_expression:
            return

        search_limit = search_engine.Limit(self.limit)
        search_result = {
            search_expression.name: search_limit.limit_data(search_expression.search(term))
        }

        names = [
            result_item.name
            for result_item in search_result[search_expression.name]
        ]
        return JsonResponse(names, safe=False)
