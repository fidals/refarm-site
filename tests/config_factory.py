
def get_usual():
    """This config includes most of corner cases"""
    return {
        'article': {'name': 'Статьи', 'alias': ''},
        'news': {'name': 'Новости', 'alias': 'news', 'default': True},
        'navigation': {'name': 'Навигация', 'alias': 'navigation'},
    }


def get_empty():
    return {
        '': {'name': '', 'alias': '', 'default': False},
    }


def get_alias_with_slashes():
    """Post aliases have slashes"""
    return {
        'article': {'name': 'Статьи', 'alias': '/'},
        'news': {'name': 'Новости', 'alias': '/news/', 'default': True},
        'navigation': {'name': 'Навигация', 'alias': 'navigation/'},
    }


def get_alias_empty():
    """Post aliases are empty"""
    return {
        'article': {'name': 'Статьи', 'alias': ''},
        'news': {'name': 'Новости', 'alias': '/', 'default': True},
        'navigation': {'name': 'Навигация', 'alias': ''},
    }
