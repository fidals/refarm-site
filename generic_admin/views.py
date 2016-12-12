from itertools import chain
from functools import partial
from typing import Iterator, Union

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
    """Mixin gives simple access to model's fields."""

    def __init__(
            self, model, relation_field_names, included_related_model_fields=None,
            excluded_related_model_fields=None, included_model_fields=None,
            excluded_model_fields=None
    ):
        self.model = model

        self.relation_field_names = relation_field_names

        self.included_related_model_fields = included_related_model_fields or {}
        self.excluded_related_model_fields = excluded_related_model_fields or {}

        self.included_model_fields = included_model_fields or []
        self.excluded_model_fields = excluded_model_fields or []

    def _get_all_fields(self, model: Model):
        return (field for field in model._meta.get_fields())

    def _get_field(self, model: Model, field_name: str) -> Field:
        return next(filter(lambda field: field.name == field_name, self._get_all_fields(model)))

    def _get_included_fields(self, model: Model, included_fields: list):
        return filter(lambda field: field.name in included_fields, self._get_all_fields(model))

    def _get_not_excluded_fields(self, model: Model, excluded_fields: list):
        return filter(lambda field: field.name not in excluded_fields, self._get_all_fields(model))

    def get_related_model_fields(self) -> Iterator[Union[str, Field]]:
        def get_fields(related_field_name):
            model = self._get_field(self.model, related_field_name).related_model

            included_fields = self.included_related_model_fields.get(related_field_name)
            excluded_fields = self.excluded_related_model_fields.get(related_field_name)

            fields = None

            if included_fields:
                fields = self._get_included_fields(model, included_fields)

            elif excluded_fields:
                fields = self._get_not_excluded_fields(model, excluded_fields)

            else:
                fields = self._get_all_fields(model)

            return related_field_name, fields

        return map(get_fields, self.relation_field_names)

    def get_model_fields(self, *args, **kwargs) -> Iterator[Field]:
        if self.included_model_fields:
            return self._get_included_fields(self.model, self.included_model_fields)

        if self.excluded_model_fields:
            return self._get_not_excluded_fields(self.model, self.excluded_model_fields)

        return self._get_all_fields(self.model)

    def value_to_python(self, model, key, value):
        # https://goo.gl/luu69S
        to_python = self._get_field(model, key).to_python
        try:
            return to_python(value)
        except ValidationError as err:
            raise ValueError(next(iter(err.messages)))


class ABSTableEditor(MultipleObjectMixin, View):
    """
    Handling CBV request, queryset logic and TableEditor fields control.
    """
    model = None
    relation_field_names = []

    field_controller = TableEditorFieldsControlMixin(model, relation_field_names)


class TableEditorGet:
    def prepare_related_model_fields(self, fields_data):
        def prepare_fields(related_field_name, fields):
            return (
                (
                    '{}_{}'.format(related_field_name, field.name),
                    F('{}__{}'.format(related_field_name, field.name))
                ) for field in fields
            )

        return dict(chain.from_iterable(map(prepare_fields, *zip(*fields_data))))

    def get_queryset(self, *args, **kwargs):
        annotate_data = self.prepare_related_model_fields(
            self.field_controller.get_related_model_fields()
        )

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
            raise ValueError('{} has not `{}` in fields'.format(
                related_model_entity, related_model_key
            ))

        python_value = self.field_controller.value_to_python(related_model_entity, related_model_key, value)

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
            raise ValueError('{} has not `{}` in fields'.format(
                product, key
            ))

        python_value = self.field_controller.value_to_python(product, key, value)

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
        ABSTableEditor
    ):
    """REST view with CRUD logic."""
    http_method_names = ['post', 'put', 'delete', 'get']


class TableEditor(ABSTableEditor):
    """Admin view for TableEditor."""
    http_method_names = ['get']
    default_filters = ['name', 'price', 'is_popular', 'is_active']

    each_context = None  # Define from Admin's site.

    def prepare_related_model_fields(self, fields_data):
        def prepare_fields(related_field_name, fields):
            capitalize_related_field_name = related_field_name.capitalize()

            return (
                ('{}_{}'.format(related_field_name, field.name),
                 '{} {}'.format(
                     capitalize_related_field_name,
                     getattr(field, 'verbose_name', field.name)))
                for field in fields
            )

        return chain.from_iterable(map(prepare_fields, *zip(*fields_data)))

    def prepare_model_fields(self, fields):
        return (
            (field.name,
             getattr(field, 'verbose_name', field.name).capitalize())
            for field in fields
        )

    def get_filter(self):
        prepared_related_model_fields = self.prepare_related_model_fields(
            self.field_controller.get_related_model_fields()
        )

        prepared_model_fields = self.prepare_model_fields(
            self.field_controller.get_model_fields()
        )

        filter_data = chain(prepared_model_fields, prepared_related_model_fields)

        return [
            {'id': 'filter-{}'.format(id_attr),
             'name': name,
             'checked': id_attr.split('_')[-1] in self.default_filters}
            for id_attr, name in filter_data
        ]

    def get(self, request, *args, **kwargs):

        context = {
            **self.each_context(request),
            'title': 'Table editor',
            'filter_fields': self.get_filter(),
        }

        return TemplateResponse(request, 'admin/table_editor.html', context)


class Tree(View, MultipleObjectMixin):
    """
    Gather JSON response for jsTree's lazy load, with category's children or
    category's products.
    """
    model = None

    # Page model names for reversing url.
    CATEGORY_PAGE_MODEL_NAME = 'categorypage'
    PRODUCT_PAGE_MODEL_NAME = 'productpage'

    def prepare_for_js_tree(self, entities):
        if not entities.exists():
            return {'text': 'У категории нет товаров.'}

        is_category = isinstance(entities.first(), self.model)
        urlconf = 'admin:{}_{}_change'.format(
            self.model._meta.app_label,
            self.CATEGORY_PAGE_MODEL_NAME if is_category else self.PRODUCT_PAGE_MODEL_NAME
        )

        # jsTree has restriction on the field's names.
        return [{
           'id': entity.id,
           'text': '[ {id} ] {name}'.format(id=entity.id, name=entity.name),
           'children': is_category,  # if False, then lazy load switch off
           'a_attr': {  # it is <a> tag's attributes
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
        entities = self.get_queryset(category_id=category_id)
        return JsonResponse(self.prepare_for_js_tree(entities), safe=False)


class RedirectToProductPage(View):
    model = None
    admin_page_product_urlconf = None
    site_page_product_urlconf = None

    def get(self, request, *args, **kwargs):
        id_, is_to_site = request.GET.get('id'), int(request.GET.get('tosite'))
        pattern_name = None
        if is_to_site:
            pattern_name = self.site_page_product_urlconf
        else:
            pattern_name = self.admin_page_product_urlconf
            id_ = self.model.objects.get(id=id_).page_id

        return HttpResponse(reverse(pattern_name, args=(id_, )))
