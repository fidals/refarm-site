from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

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
    correct_category_id.short_description = _('Category ID')


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
    readonly_fields = ['id', 'correct_parent_id']

    def correct_parent_id(self, obj):
        """Needed for correct short_description attr"""
        return obj.parent_id

    correct_parent_id.short_description = _('Parent ID')


class ImageInline(GenericStackedInline):
    model = Image
    extra = 1
    readonly_fields = ['current_image']
    verbose_name = _('Image')
    fieldsets = (
        (None, {
            'classes': ('primary-chars', ),
            'fields': (
                'current_image',
                'image',
                ('title', 'description'),
                ('slug', 'is_main'),
            ),
        }),
    )

    def current_image(self, obj):
        return format_html(
            '<img src="{url}" class="img-responsive images-item">',
            url=obj.image.url
        )

    current_image.short_description = _('current image')
