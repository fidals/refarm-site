from django.contrib import admin
from django.conf.urls import url
from django.template.response import TemplateResponse


class TableEditor(admin.AdminSite):

    # Fields for TableEditor filters:
    FILTER_FIELDS = (
        {
            'id': 'filter-name',
            'name': 'Название',
            'checked': True,
        },
        {
            'id': 'filter-title',
            'name': 'Заголовок',
            'checked': False,
        },
        {
            'id': 'filter-category_name',
            'name': 'Категория',
            'checked': True,
        },
        {
            'id': 'filter-price',
            'name': 'Цена',
            'checked': True,
        },
        {
            'id': 'filter-purchase_price',
            'name': 'Закупочная цена',
            'checked': False,
        },
        {
            'id': 'filter-is_active',
            'name': 'Активность',
            'checked': True,
        },
        {
            'id': 'filter-is_popular',
            'name': 'Топ',
            'checked': True,
        },
        {
            'id': 'filter-in_stock',
            'name': 'Наличие',
            'checked': False,
        },
    )

    def get_urls(self):
        original_urls = super(TableEditor, self).get_urls()

        return [
            url(r'^editor/$', self.admin_view(self.table_editor_view), name='editor'),
            *original_urls
        ]

    def table_editor_view(self, request):
        context = {
            # Include common variables for rendering the admin template.
            **self.each_context(request),
            # Anything else you want in the context...
            'title': 'Table editor',
            'filter_fields': self.FILTER_FIELDS,
        }

        return TemplateResponse(request, 'admin/table_editor.html', context)
