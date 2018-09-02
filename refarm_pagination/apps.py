from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PaginationConfig(AppConfig):
    name = 'refarm_pagination'
    verbose_name = _('refarm_pagination')
