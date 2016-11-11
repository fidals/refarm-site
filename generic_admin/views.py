from itertools import chain
from functools import partial
from collections import ChainMap
from typing import Iterator

from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.db.models import F, ObjectDoesNotExist, Model, Field
from django.views.generic import View
from django.views.generic.list import MultipleObjectMixin
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse, QueryDict
from django.template.response import TemplateResponse


class TableEditorFieldsControlMixin:
    """Mixin for simplifies to work with model's fields."""

    relation_field_names = []
    include_related_model_fields = exclude_related_model_fields = {None: []}
    include_model_fields = exclude_model_fields = []

    def get_all_fields(self, model: Model):
        return (field for field in model._meta.get_fields())

    def get_field(self, model: Model, field_name: str) -> Field:
        return next(filter(lambda field: field.name == field_name, self.get_all_fields(model)))

    def get_include_fields(self, model: Model, include_fields: list):
        return filter(lambda field: field.name in include_fields, self.get_all_fields(model))

    def get_not_exclude_fields(self, model: Model, exclude_fields: list):
        return filter(lambda field: field.name not in exclude_fields, self.get_all_fields(model))

    def get_related_model_fields(self, related_field_name: str, *args, **kwargs) -> Iterator[Field]:
        model = self.get_field(self.model, related_field_name).related_model

        include_fields = self.include_related_model_fields.get(related_field_name)
        exclude_fields = self.exclude_related_model_fields.get(related_field_name)

        if include_fields:
            return self.get_include_fields(model, include_fields)

        if exclude_fields:
            return self.get_not_exclude_fields(model, exclude_fields)

        return self.get_all_fields(model)

    def get_model_fields(self, *args, **kwargs) -> Iterator[Field]:
        if self.include_model_fields:
            return self.get_include_fields(self.model, self.include_model_fields)

        if self.exclude_model_fields:
            return self.get_not_exclude_fields(self.model, self.exclude_model_fields)

        return self.get_all_fields(self.model)

    def value_to_python(self, model, key, value):
        # https://goo.gl/luu69S
        to_python = self.get_field(model, key).to_python
        try:
            return to_python(value)
        except ValidationError as err:
            raise ValueError(next(iter(err.messages)))


class TableEditorMixin(TableEditorFieldsControlMixin, MultipleObjectMixin, View):
    """
    Handling CBV request, queryset logic and TableEditor fields control.
    """


class TableEditorGet:
    def get_related_model_fields(self, related_field_name: str, *args, **kwargs):
        fields = super(TableEditorGet, self).get_related_model_fields(
            related_field_name, *args, **kwargs)

        return {
            '{}_{}'.format(related_field_name, field.name):
                F('{}__{}'.format(related_field_name, field.name))
            for field in fields
        }

    def get_queryset(self, *args, **kwargs):
        annotate_data = dict(ChainMap(*(
            self.get_related_model_fields(field_name)
            for field_name in self.relation_field_names
        )))

        return (
            super(TableEditorGet, self)
                .get_queryset()
                .select_related(*self.relation_field_names)
                .annotate(**annotate_data)
        )

    def get(self, request, *args, **kwargs):
        products = self.get_queryset().values()
        return JsonResponse(list(products), safe=False)


class TableEditorPut:
    pattern_to_update_related_model = {}
    pattern_to_update_model = {}

    def put(self, request, *args, **kwargs):
        body = {k: v[0] for k, v in dict(QueryDict(request.body)).items()}

        try:
            product = self.model.objects.get(id=body['id'])

        except KeyError:
            return HttpResponse(content='Request body has not `id` param.', status=422)
        except ObjectDoesNotExist:
            return HttpResponse(
                'Product with id={} does not exists.'.format(body['id']), status=422)

        try:
            with transaction.atomic():
                for k, v in body.items():
                    if any(field_name in k for field_name in self.relation_field_names):
                        self.update_related_model(product, k, v)
                    else:
                        self.update_model(product, k, v)
                self.save(product)
        except ValueError as err:
            return JsonResponse({
                'message': next(iter(err.args)),
                'field': k,
            }, status=422)

        return HttpResponse('Product was updated.')

    def update_related_model(self, product, key, value):
        related_model_name = next(filter(partial(key.startswith), self.relation_field_names))
        related_model_entity = getattr(product, related_model_name)

        related_model_key = key.replace('{}_'.format(related_model_name), '')
        if not hasattr(related_model_entity, related_model_key):
            return

        python_value = self.value_to_python(related_model_entity, related_model_key, value)

        related_model_strategy = self.pattern_to_update_related_model.get(related_model_name, {})

        if related_model_key in related_model_strategy:
            related_model_strategy[related_model_key](
                product=product, related_model_entity=related_model_entity,
                related_model_value=python_value,
            )
        else:
            setattr(related_model_entity, related_model_key, python_value)

    def update_model(self, product, key, value):
        if not hasattr(product, key):
            return

        python_value = self.value_to_python(product, key, value)

        if key in self.pattern_to_update_model:
            self.pattern_to_update_model[key](
                product=product, value=python_value)
        else:
            setattr(product, key, python_value)

    def save(self, product):
        product.save()
        for field in self.relation_field_names:
            getattr(product, field).save()


class TableEditorDelete:
    def delete(self, request, *args, **kwargs):
        try:
            id_ = QueryDict(request.body)['id']
            product = self.model.objects.get(id=id_)
        except KeyError:
            return HttpResponse(content='Request body has not `id` param.', status=422)
        except ObjectDoesNotExist:
            return HttpResponse('Product with id={} does not exists.'.format(id_), status=422)

        product.delete()

        return HttpResponse('Product {} was deleted.'.format(product.id))


class TableEditorPost:
    def post(self, request, *args, **kwargs):
        """
        TODO: Logic for create Product is required
        http://youtrack.stkmail.ru/issue/dev-787
        """


@method_decorator(staff_member_required, name='dispatch')
class TableEditorAPI(
    TableEditorPost,
    TableEditorGet,
    TableEditorPut,
    TableEditorDelete,
    TableEditorMixin
):
    """REST view with CRUD logic."""
    http_method_names = ['post', 'put', 'delete', 'get']


class TableEditor(TableEditorMixin):
    """Admin view for TableEditor."""
    http_method_names = ['get']
    default_filters = ['name', 'price', 'is_popular', 'is_active']

    each_context = None  # Define from Admin's site.

    def get_related_model_fields(self, related_field_name: str, *args, **kwargs):
        fields = super(TableEditor, self).get_related_model_fields(
            related_field_name, *args, **kwargs)

        capitalize_related_field_name = related_field_name.capitalize()
        return (
            ('{}_{}'.format(related_field_name, field.name),
             '{} {}'.format(
                 capitalize_related_field_name,
                 getattr(field, 'verbose_name', field.name)))
            for field in fields
        )

    def get_model_fields(self, *args, **kwargs):
        fields = super(TableEditor, self).get_model_fields(*args, **kwargs)

        return (
            (field.name,
             getattr(field, 'verbose_name', field.name).capitalize())
            for field in fields
        )

    def gather_filter_data(self):
        related_model_fields_data = chain.from_iterable(
            self.get_related_model_fields(field_name)
            for field_name in self.relation_field_names
        )

        model_fields_data = self.get_model_fields()

        filter_data = chain(model_fields_data, related_model_fields_data)

        return [
            {'id': 'filter-{}'.format(id_attr),
             'name': name,
             'checked': id_attr.split('_')[-1] in self.default_filters}
            for id_attr, name in filter_data
        ]

    def get(self, request, *args, **kwargs):
        filters = self.gather_filter_data()

        context = {
            **self.each_context(request),
            'title': 'Table editor',
            'filter_fields': filters,
        }

        return TemplateResponse(request, 'admin/table_editor.html', context)


class Tree(View, MultipleObjectMixin):
    """
    Gather JSON response for jsTree's lazy load, with category's children or
    category's products.
    """
    model = None

    # Page model names for reversing url.
    category_page_model_name = 'categorypage'
    product_page_model_name = 'productpage'

    def gather_js_tree_data(self, entities):
        if not entities.exists():
            return {'text': 'У категории нет товаров.'}

        is_category = isinstance(entities.first(), self.model)
        urlconf = 'admin:{}_{}_change'.format(
            self.model._meta.app_label,
            self.category_page_model_name if is_category else self.product_page_model_name
        )

        # jsTree has restriction on the field's names.
        return [{
           'id': entity.id,
           'text': '[ {id} ] {name}'.format(id=entity.id, name=entity.name),
           'children': is_category,  # if False, then lazy load switch off
           'a_attr': {  # it is "a" tag's attribute
               'href-site-page': entity.get_absolute_url(),
               'href-admin-page': reverse(urlconf, args=(entity.page_id,)),
               'search-term': entity.name,
           }
        } for entity in entities.iterator()]

    def get_queryset(self, category_id=None, *args, **kwargs):
        if not category_id:
            return self.model.objects.root_nodes().order_by('page__position')

        category = self.model.objects.get(id=category_id)
        children = category.children.all()
        products = category.products.all()
        return children if children.exists() else products

    def get(self, request, *args, **kwargs):
        category_id = request.GET.get('id')
        data = self.get_queryset(category_id=category_id)
        return JsonResponse(self.gather_js_tree_data(data), safe=False)
