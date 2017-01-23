from django.contrib import admin
from django.contrib.redirects.models import Redirect
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse
from django.db.models import QuerySet, F
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from generic_admin import filters, inlines


class PermissionsControl(admin.ModelAdmin):
    """Roughly defines user rights."""
    add = True
    change = True
    delete = True

    def has_add_permission(self, request):
        return self.add

    def has_change_permission(self, request, obj=None):
        return self.change

    def has_delete_permission(self, request, obj=None):
        return self.delete


class ChangeItemsStateActions(admin.ModelAdmin):
    @staticmethod
    def after_action_message(updated_rows):
        return (
            '1 {}'.format(_('item was'))
            if updated_rows == 1 else
            '{} {}'.format(updated_rows, _('items were'))
        )

    def make_items_active(self, request, queryset):
        updated_rows = queryset.update(is_active=1)
        message_prefix = self.after_action_message(updated_rows)

        self.message_user(request, '{} {}.'.format(message_prefix, _('marked as active')))

    def make_items_non_active(self, request, queryset):
        updated_rows = queryset.update(is_active=0)
        message_prefix = self.after_action_message(updated_rows)

        self.message_user(request, '{} {}.'.format(message_prefix, _('marked as non-active')))

    make_items_active.short_description = _('Make active')
    make_items_non_active.short_description = _('Make inactive')


class AutoCreateRedirects(admin.ModelAdmin):
    """Create new redirect link after slug field change."""
    def save_model(self, request, obj, form, change):
        if change and 'slug' in form.changed_data:
            old_obj = type(obj).objects.get(id=obj.id)
            Redirect.objects.create(
                site=get_current_site(request), old_path=old_obj.url, new_path=obj.url)

        super(AutoCreateRedirects, self).save_model(request, obj, form, change)


class AbstractPage(ChangeItemsStateActions):
    """Generic class for each page."""

    actions = ['make_items_active', 'make_items_non_active']
    list_display_links = ['name']
    list_filter = ['is_active', filters.HasContent, filters.HasImages]
    save_on_top = True
    search_fields = ['id', 'name', 'slug']

    def get_queryset(self, request):
        return super(AbstractPage, self).get_queryset(request).select_related('parent')

    def custom_parent(self, obj, urlconf=None):
        parent = obj.parent

        if not parent:
            return

        urlconf = urlconf or '{}:{}_{}_change'.format(
            self.admin_site.name,
            self.model._meta.app_label,
            self.model._meta.model_name
        )

        url = reverse(urlconf, args=(parent.id,))

        return format_html(
            '<a href="{url}">{parent}</a>',
            parent=parent,
            url=url
        )

    custom_parent.admin_order_field = 'parent__name'
    custom_parent.short_description = _('Parent')


class PageWithoutModels(AbstractPage):
    list_display = ['id', 'name', 'slug', 'date_published', 'custom_parent', 'is_active']
    readonly_fields = ['id', 'correct_parent_id']
    inlines = [inlines.ImageInline]

    def correct_parent_id(self, obj):
        """Needed for correct short_description attr"""
        return obj.parent_id

    correct_parent_id.short_description = _('Parent ID')


class PageWithModels(AbstractPage, PermissionsControl, AutoCreateRedirects):
    readonly_fields = ['id', 'model_id']
    fieldsets = (
        ('Дополнительные характеристики', {
            'classes': ('seo-chars',),
            'fields': (
                'id',
                'is_active',
                ('name', 'slug'),
                'date_published',
                'menu_title',
                'seo_text',
                'position',
            )
        }),
        ('Параметры страницы', {
            'classes': ('secondary-chars',),
            'fields': (
                'h1',
                'title',
                'keywords',
                'description',
                'content'
            )
        })
    )

    @staticmethod
    def assert_is_proxy(qs: QuerySet):
        """Is it proxy for only one related model?"""
        count = qs.distinct('related_model_name').count()
        assert count <= 1, 'You should split your model pages by proxy, before register it.'

    @classmethod
    def add_reference_to_field_on_related_model(cls, qs: QuerySet, **kwargs):
        cls.assert_is_proxy(qs)

        modified_qs = qs.all()

        if qs.distinct('related_model_name').count() == 1:
            related_model_name = qs.first().related_model_name
            modified_qs = modified_qs.annotate(**{
                key: F('{}__{}'.format(related_model_name, value))
                for key, value in kwargs.items()
            })

        return modified_qs

    def model_id(self, obj):
        return obj.model.id

    def get_search_fields(self, request):
        """https://goo.gl/4jVdgn"""
        self.assert_is_proxy(self.model.objects.all())

        if not self.search_fields:
            model_related_name = self.model.objects.first().related_model_name
            self.search_fields = ['{}__id'.format(model_related_name), 'name', 'parent__name']
        return self.search_fields
