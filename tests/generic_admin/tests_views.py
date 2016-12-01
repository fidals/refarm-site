from functools import partial
from urllib.parse import urlencode

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.test import TestCase
from django.http import HttpResponse

from generic_admin import views
from tests.models import TestEntityWithRelations, RelatedEntity, AnotherRelatedEntity


def related_entity_name_strategy(**kwargs):
    return kwargs


class GenericTableEditor:
    model = TestEntityWithRelations
    relation_field_names = ['related_entity', 'another_related_entity']

    excluded_model_fields = ['id', 'is_active']
    excluded_related_model_fields = {
        'another_related_entity': ['is_active'],
    }
    included_related_model_fields = {
        'related_entity': [
            'name'
        ],
    }


    field_controller = views.TableEditorFieldsControlMixin(
        model,
        relation_field_names=relation_field_names,
        excluded_model_fields=excluded_model_fields,
        included_related_model_fields=included_related_model_fields,
        excluded_related_model_fields=excluded_related_model_fields
    )


class TableEditorAPI(GenericTableEditor, views.TableEditorAPI):
    pattern_to_update_related_model = {
        'related_entity': {
            'name': related_entity_name_strategy
        }
    }


class TestsTableEditorFieldsControl(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestsTableEditorFieldsControl, cls).setUpClass()
        cls.model = TableEditorAPI.model
        cls.field_controller = TableEditorAPI.field_controller

        cls.relation_field_names = TableEditorAPI.relation_field_names
        cls.excluded_model_fields = TableEditorAPI.excluded_model_fields
        cls.included_related_model_fields = TableEditorAPI.included_related_model_fields
        cls.excluded_related_model_fields = TableEditorAPI.excluded_related_model_fields


    def test_get_all_field(self):
        field_count = len(list(self.field_controller._get_all_fields(self.model)))
        self.assertEqual(field_count, 5)

    def test_get_field(self):
        """Get only one field from model."""
        field_name = self.field_controller._get_field(self.model, 'name')

        self.assertTrue(isinstance(field_name, models.Field))
        self.assertEqual(field_name.model, self.model)

    def test_get_not_excluded_field(self):
        fields = list(self.field_controller._get_not_excluded_fields(
            self.model, self.excluded_model_fields))

        self.assertEqual(len(fields), 3)
        self.assertTrue(all(
            field.name not in self.excluded_model_fields
            for field in fields
        ))

    def test_get_related_model_fields(self):
        related_entity, another_related_entity = list(
            self.field_controller.get_related_model_fields())

        self.assertEqual(len(related_entity), 2)
        self.assertEqual(len(list(related_entity[1])), 1)
        self.assertEqual(len(another_related_entity), 2)
        self.assertEqual(len(list(another_related_entity[1])), 3)

        self.assertEqual(related_entity[0], self.relation_field_names[0])
        self.assertEqual(another_related_entity[0], self.relation_field_names[1])

        self.assertTrue(all(
            field.name not in self.excluded_related_model_fields
            for field in related_entity[1]
        ))
        self.assertTrue(all(
            field.name not in self.included_related_model_fields
            for field in another_related_entity[1]
        ))

    def test_get_model_fields(self):
        fields = list(self.field_controller.get_model_fields())

        self.assertEqual(len(fields), 3)
        self.assertTrue(all(
            field.name not in self.excluded_model_fields
            for field in fields
        ))

    def test_value_to_python(self):
        get_val = partial(self.field_controller.value_to_python, self.model, 'is_active')

        first_falsy = get_val('0')
        second_falsy = get_val('False')

        first_truthy = get_val('1')
        second_truthy = get_val('True')

        self.assertIs(first_falsy, second_falsy, False)
        self.assertIs(first_truthy, second_truthy, True)


class TestsTableEditorApi(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestsTableEditorApi, cls).setUpClass()

        cls.username = 'admin'
        cls.email = 'admin@admin.com'
        cls.password = 'asdfjkl'

        cls.entities_count = 10

        for i in range(cls.entities_count):
            name = 'test entity #{}'.format(i)
            is_active = bool(i%2)
            TestEntityWithRelations.objects.create(
                name=name,
                is_active=is_active,
                related_entity=RelatedEntity.objects.create(
                    name='related {}'.format(name),
                    is_active=is_active
                ),
                another_related_entity=AnotherRelatedEntity.objects.create(
                    name='another related {}'.format(name),
                    is_active=is_active,
                )
            )

        cls.urlconf_name = 'test_table_editor_api'

    @classmethod
    def tearDownClass(cls):
        super(TestsTableEditorApi, cls).tearDownClass()
        TestEntityWithRelations.objects.all().delete()
        RelatedEntity.objects.all().delete()
        AnotherRelatedEntity.objects.all().delete()

    def setUp(self):
        self.user = User.objects.create_superuser(self.username, self.email, self.password)
        self.client.login(username=self.username, password=self.password)

    def tearDown(self):
        self.user.delete()

    def test_get(self):
        response = self.client.get(reverse(self.urlconf_name))

        self.assertEqual(self.entities_count, len(response.json()))
        self.assertTrue(isinstance(response, HttpResponse))

    def test_put(self):
        entity = TestEntityWithRelations.objects.all().order_by('id').first()

        new_name = 'Newly come up name'
        new_is_active = not entity.another_related_entity.is_active

        response = self.client.put(
            reverse(self.urlconf_name),
            data=urlencode({
                'id': entity.id,
                'name': new_name,
                'another_related_entity_is_active': new_is_active
            })
        )

        self.assertEqual(response.status_code, 200)

        updated_entity = TestEntityWithRelations.objects.get(id=entity.id)

        self.assertNotEqual(entity.name, updated_entity.name)
        self.assertNotEqual(
            entity.another_related_entity.is_active,
            updated_entity.another_related_entity.is_active
        )

        self.assertEqual(new_name, updated_entity.name)
        self.assertEqual(
            new_is_active,
            updated_entity.another_related_entity.is_active
        )

    def test_delete(self):
        entity_id = TestEntityWithRelations.objects.all().order_by('id').first().id

        response = self.client.delete(
            reverse(self.urlconf_name),
            data=urlencode({
                'id': entity_id,
            })
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(TestEntityWithRelations.objects.filter(id=entity_id))
