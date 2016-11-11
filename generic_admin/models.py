from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from generic_admin import mixins, filters


class CustomPageAdmin(mixins.PageWithoutModels, mixins.PermissionsControl):
    delete = False
    add = False

    fieldsets = (
        ('Дополнительные характеристики', {
            'classes': ('seo-chars',),
            'fields': (
                ('id', 'is_active'),
                'date_published',
                '_menu_title',
                'seo_text',
                'position',
                ('parent', 'correct_parent_id')
            )
        }),
        ('Параметры страницы', {
            'classes': ('secondary-chars',),
            'fields': (
                ('h1', '_title'),
                ('keywords', 'id'),
                'description',
                'content'
            )
        })
    )


class FlatPageAdmin(mixins.PageWithoutModels, mixins.AutoCreateRedirects):
    fieldsets = (
        ('Дополнительные характеристики', {
            'classes': ('seo-chars',),
            'fields': (
                ('id', 'is_active'),
                'date_published',
                'slug',
                '_menu_title',
                'seo_text',
                'position',
                ('parent', 'correct_parent_id')
            )
        }),
        ('Параметры страницы', {
            'classes': ('secondary-chars',),
            'fields': (
                ('h1', '_title'),
                'keywords',
                'description',
                'content'
            )
        })
    )


class ProductPageAdmin(mixins.PageWithModels):
    category_page_model = None
    list_filter = ['is_active', filters.PriceRange, filters.HasContent, filters.HasImages]
    list_display = ['model_id', 'h1', 'custom_parent', 'price', 'links', 'is_active']

    def get_queryset(self, request):
        qs = super(ProductPageAdmin, self).get_queryset(request)
        return self.add_reference_to_field_on_related_model(
            qs, _product_price='price', _product_id='id')

    def price(self, obj):
        return obj.model.price

    price.short_description = _('Price')
    price.admin_order_field = '_product_price'

    def custom_parent(self, obj, urlconf=None):
        assert self.category_page_model, 'Define category_page_model attr, for order columns'
        urlconf = '{}:{}_{}_change'.format(
            self.admin_site.name,
            self.category_page_model._meta.app_label,
            self.category_page_model._meta.model_name
        )
        return super(ProductPageAdmin, self).custom_parent(obj, urlconf)

    custom_parent.admin_order_field = 'parent__h1'
    custom_parent.short_description = _('Parent')

    mixins.PageWithModels.model_id.admin_order_field = '_product_id'

    def links(self, obj):
        return format_html(
            '''
            <a href="{site_url}" class="field-link" title="Посмотреть на сайте" target="_blank">
              <i class="fa fa-link" aria-hidden="true"></i>
            </a>
            '''.format(site_url=obj.url))

    links.short_description = _('Link')


class CategoryPageAdmin(mixins.PageWithModels):
    list_display = ['model_id', 'h1', 'custom_parent', 'is_active']

    def get_queryset(self, request):
        qs = super(CategoryPageAdmin, self).get_queryset(request)
        return self.add_reference_to_field_on_related_model(qs, _category_id='id')

    mixins.PageWithModels.model_id.admin_order_field = '_category_id'
