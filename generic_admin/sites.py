from django.contrib import admin
from django.conf.urls import url

from generic_admin import views


class SiteWithTableEditor(admin.AdminSite):
    table_editor_view = views.TableEditor

    def get_urls(self):
        original_urls = super(SiteWithTableEditor, self).get_urls()

        return [
            url(r'^editor/$',
                self.admin_view(self.table_editor_view.as_view(each_context=self.each_context)),
                name='editor'),
            *original_urls
        ]
