from django.contrib import admin

from pages.models import CustomPage, ModelPage, FlatPage


class PageAdmin(admin.ModelAdmin):
    fields = ['_title', 'slug', '_parent', 'is_active', 'position',
              'h1', 'keywords', 'description', 'content', 'seo_text']
    list_display = ['id', '_title', 'slug']
    list_display_links = ['_title']
    search_fields = ['_title', 'slug']
