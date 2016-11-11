from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.utils.html import format_html

from images.models import Image


class ProductInline(admin.StackedInline):
    model = None
    can_delete = False
    readonly_fields = ['id', 'correct_category_id']
    fieldsets = ((None, {
        'classes': ('primary-chars', ),
        'fields': (
            ('name', 'id'),
            ('category', 'correct_category_id'),
            ('price', 'in_stock', 'is_popular'),
        )
    }),)

    def correct_category_id(self, obj):
        """Needed for correct short_description attr"""
        return obj.category_id
    correct_category_id.short_description = 'Category ID'


class CategoryInline(admin.StackedInline):
    model = None
    can_delete = False
    fieldsets = ((None, {
        'classes': ('primary-chars', ),
        'fields': (
            ('name', 'id'),
            ('parent', 'correct_parent_id'),
        )
    }),)

    def correct_parent_id(self, obj):
        """Needed for correct short_description attr"""
        return obj.parent_id
    correct_parent_id.short_description = 'Parent ID'

    readonly_fields = ['id', 'correct_parent_id']


class ImageInline(GenericStackedInline):
    model = Image
    extra = 1
    readonly_fields = ['picture']
    verbose_name = 'Image'
    fieldsets = (
        (None, {
            'classes': ('primary-chars', ),
            'fields': (
                ('picture', 'image'),
                ('slug', '_title', 'is_main'),
                ('description', ),
            ),
        }),
    )

    def picture(self, obj):
        return format_html(
            '<img src="{url}" class="images-item">',
            url=obj.image.url
        )
