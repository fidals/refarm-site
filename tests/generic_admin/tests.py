from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.redirects.models import Redirect
from django.test import TestCase
from django.http.request import HttpRequest

from generic_admin.admin.sites import TableEditor
from generic_admin.admin.mixins import (
    PermissionsControl, ChangeItemsStateActions, AutoCreateRedirects)

from tests.models import TestEntity


class MockSuperUser:
    def has_perm(self, perm):
        return True

request = HttpRequest()
request.user = MockSuperUser()
request.session = 'session'
messages = FallbackStorage(request)
request._messages = messages


class TestMixins(TestCase):
    def setUp(self):
        self.entity = TestEntity.objects.create(name='Test')
        self.site = TableEditor()

    def test_permissions_control(self):
        ma = PermissionsControl(TestEntity, self.site)
        permission_checks = [
            ma.has_add_permission, ma.has_change_permission, ma.has_delete_permission
        ]

        for check in permission_checks:
            self.assertTrue(check(request))

        ma.add = False
        ma.delete = False
        ma.change = False

        for check in permission_checks:
            self.assertFalse(check(request))

    def test_change_items_state_actions(self):
        ma = ChangeItemsStateActions(TestEntity, self.site)

        ma.make_items_non_active(request, TestEntity.objects.all())
        self.assertFalse(TestEntity.objects.first().is_active)

        ma.make_items_active(request, TestEntity.objects.all())
        self.assertTrue(TestEntity.objects.first().is_active)

    def test_auto_create_redirects(self):
        class TestForm:
            changed_data = ['slug']

        ma = AutoCreateRedirects(TestEntity, self.site)
        obj = TestEntity.objects.first()
        new_slug = 'ololo'

        obj.slug = new_slug
        ma.save_model(request, obj=obj, form=TestForm(), change=True)

        redirect = Redirect.objects.first()
        self.assertEqual(Redirect.objects.count(), 1)
        self.assertEqual(redirect.old_path, '/so-mock-wow/')
        self.assertEqual(redirect.new_path, new_slug)
