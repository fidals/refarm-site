from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.redirects.models import Redirect
from django.test import TestCase
from django.http.request import HttpRequest

from generic_admin.sites import SiteWithTableEditor
from generic_admin.mixins import PermissionsControl, ChangeItemsStateActions, AutoCreateRedirects

from tests.models import MockEntity


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
        self.entity = MockEntity.objects.create(name='Test')
        self.site = SiteWithTableEditor()

    def test_permissions_control(self):
        ma = PermissionsControl(MockEntity, self.site)  # ModelAdmin
        permission_checks = [
            ma.has_add_permission, ma.has_change_permission, ma.has_delete_permission
        ]

        for check in permission_checks:
            self.assertTrue(check(request))

        ma.add, ma.delete, ma.change = [False] * 3

        for check in permission_checks:
            self.assertFalse(check(request))

    def test_change_items_state_actions(self):
        ma = ChangeItemsStateActions(MockEntity, self.site)  # ModelAdmin

        ma.make_items_non_active(request, MockEntity.objects.all())
        self.assertFalse(MockEntity.objects.first().is_active)

        ma.make_items_active(request, MockEntity.objects.all())
        self.assertTrue(MockEntity.objects.first().is_active)

    def test_auto_create_redirects(self):
        class TestForm:
            changed_data = ['slug']

        ma = AutoCreateRedirects(MockEntity, self.site)  # ModelAdmin
        obj = MockEntity.objects.first()
        new_slug = 'ololo'

        obj.slug = new_slug
        ma.save_model(request, obj=obj, form=TestForm(), change=True)
        redirect = Redirect.objects.first()

        self.assertEqual(Redirect.objects.count(), 1)
        self.assertEqual(redirect.old_path, '/so-mock-wow/')
        self.assertEqual(redirect.new_path, new_slug)
