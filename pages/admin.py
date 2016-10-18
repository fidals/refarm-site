from django.contrib import admin

from pages.models import CustomPage, ModelPage, FlatPage


class PageAdmin(admin.ModelAdmin):
    fields = ['title', 'slug', '_parent', 'is_active', 'position',
              '_h1', 'keywords', 'description', 'content', 'seo_text']
    list_display = ['id', 'title', 'slug']
    list_display_links = ['title']
    search_fields = ['title', 'slug']
