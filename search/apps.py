from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SearchConfig(AppConfig):
    name = 'search'
    verbose_name = _('search')
