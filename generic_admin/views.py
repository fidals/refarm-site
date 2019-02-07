from itertools import chain
from typing import Iterator, Tuple

from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F, ObjectDoesNotExist, Model, Field
from django.http import HttpResponse, JsonResponse, QueryDict
from django.template.response import TemplateResponse
from django.views.generic import View
from django.views.generic.list import MultipleObjectMixin
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _


def get_request_body(request):
    return {k: v[0] for k, v in dict(QueryDict(request.body)).items()}

RelatedModelField = Field


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

    def get_related_model(self, related_field_name: str) -> Model:
        return self._get_field(self.model, related_field_name).related_model

    def get_related_model_fields(self) -> Iterator[Tuple[RelatedModelField, Iterator[Field]]]:
        def get_fields(related_field_name):
            model_fields = self._get_field(self.model, related_field_name)
            model = model_fields.related_model

            included_fields = self.included_related_model_fields.get(related_field_name)
            excluded_fields = self.excluded_related_model_fields.get(related_field_name)

            if included_fields:
                fields = self._get_included_fields(model, included_fields)

            elif excluded_fields:
                fields = self._get_not_excluded_fields(model, excluded_fields)

            else:
                fields = self._get_all_fields(model)

            return model_fields, fields

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
    add_entity_form = None  # Defined from Client side.
    page_creation = False  # Defined create or not Page related to new Entity.
    relation_field_names = []
    field_controller = TableEditorFieldsControlMixin(model, relation_field_names)


class TableEditorGet:
    def prepare_related_model_fields(self, fields_data):
        def prepare_fields(related_model_field, fields):
            related_model = related_model_field.related_model
            return (
                (
                    '{}_{}'.format(related_model._meta.model_name, field.name),
                    F('{}__{}'.format(related_model_field.name, field.name))
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
        body = get_request_body(request)

        try:
            entity = self.model.objects.get(id=body['id'])
        except KeyError:
            return HttpResponse(content='Request body has no `id` param.', status=422)
        except ObjectDoesNotExist:
            return HttpResponse(
                'Object with id={} doesn`t exist.'.format(body['id']), status=422)

        try:
            with transaction.atomic():
                for k, v in body.items():
                    if any(field_name in k for field_name in self.relation_field_names):
                        self.update_related_model(entity, k, v)
                    else:
                        self.update_model(entity, k, v)
                self.save(entity)
        except ValueError as err:
            return JsonResponse({
                'message': next(iter(err.args)),
                'field': k,
            }, status=422)

        return HttpResponse('Entity was updated.')

    def update_related_model(self, entity, key, value):
        model_name = next(filter(key.startswith, self.relation_field_names))
        model_entity = getattr(entity, model_name)
        model_key = key.replace('{}_'.format(model_name), '')

        if not model_entity:
            raise ValueError(f'{entity} doesn`t have any {model_name}. Create {model_name} and assign to the {entity}.')

        if not hasattr(model_entity, model_key):
            raise ValueError(f'{model_entity} doesn`t have `{model_key}` field.')

        python_value = self.field_controller.value_to_python(model_entity, model_key, value)
        model_strategy = self.pattern_to_update_related_model.get(model_name, {})

        if model_key in model_strategy:
            model_strategy[model_key](
                entity=entity, related_model_entity=model_entity,
                related_model_value=python_value,
            )
        else:
            setattr(model_entity, model_key, python_value)

    def update_model(self, entity, key, value):
        if not hasattr(entity, key):
            raise ValueError('{} hasn`t `{}` field.'.format(entity, key))

        python_value = self.field_controller.value_to_python(entity, key, value)

        if key in self.pattern_to_update_model:
            self.pattern_to_update_model[key](
                entity=entity, value=python_value)
        else:
            setattr(entity, key, python_value)

    def save(self, entity):
        entity.save()
        for field in self.relation_field_names:
            getattr(entity, field).save()


class TableEditorDelete:
    def delete(self, request, *args, **kwargs):
        try:
            id_ = QueryDict(request.body)['id']
            entity = self.model.objects.get(id=id_)
        except KeyError:
            return HttpResponse(content='Request body has no `id` param.', status=422)
        except ObjectDoesNotExist:
            return HttpResponse('Object with id={} doesn`t exist.'.format(id_), status=422)

        entity.delete()

        return HttpResponse('Object {} was deleted.'.format(entity.id))


class TableEditorPost:
    def post(self, request, *args, **kwargs):
        params = get_request_body(request)

        with transaction.atomic():
            for k, v in params.items():
                if any(related_field_name in k for related_field_name in self.relation_field_names):
                    related_model = self.field_controller.get_related_model(k)
                    params[k] = related_model.objects.get(name=v)

            new_object = self.model.objects.create(**params)

            if self.page_creation:
                model_page = self.field_controller.get_related_model('page')
                page = model_page.objects.create(name=params['name'])
                new_object.page = page

            new_object.save()

        return HttpResponse('New entity was created.')


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
        def prepare_fields(related_model_field, fields):
            related_model = related_model_field.related_model
            return (
                ('{}_{}'.format(related_model_field.name, field.name),
                 '{}: {}'.format(
                     related_model._meta.verbose_name,
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
        def get_second_el(arr):
            return arr[1]

        prepared_related_model_fields = sorted(self.prepare_related_model_fields(
            self.field_controller.get_related_model_fields()
        ), key=get_second_el)

        prepared_model_fields = sorted(self.prepare_model_fields(
            self.field_controller.get_model_fields()
        ), key=get_second_el)

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
            'title': _('Table editor'),
            'filter_fields': self.get_filter(),
            'add_entity_form': self.add_entity_form(),
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
            return {'text': 'This Category has no Products.'}

        is_category = isinstance(entities.first(), self.model)
        urlconf = 'admin:{}_{}_change'.format(
            self.model._meta.app_label,
            self.CATEGORY_PAGE_MODEL_NAME if is_category else self.PRODUCT_PAGE_MODEL_NAME
        )

        # jsTree has restriction on the field's names.
        return [{
           'id': entity.id,
           'text': entity.get_admin_tree_title(),
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
        if is_to_site:
            pattern_name = self.site_page_product_urlconf
        else:
            pattern_name = self.admin_page_product_urlconf
            id_ = self.model.objects.get(id=id_).page_id

        return HttpResponse(reverse(pattern_name, args=(id_, )))
