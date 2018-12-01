from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TestUtilsConfig(AppConfig):
    name = 'refarm_test_utils'
    verbose_name = _(name)
