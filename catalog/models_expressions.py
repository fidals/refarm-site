from django.db.models import Func


class Substring(Func):
    function = 'substring'
    arity = 2


