#Refarm blog
Provides base site blog functionality to your Django project.

## Intallation

1. Install refarm-blog app in your Django project

```pip install refarm-blog```
2. Add projects types in your Django projects settings file:

```
# [your_projects_root]/settings.py
APP_BLOG_PAGE_TYPES = {
    'article': {'name': 'Arcticles', 'alias': ''},
    'news': {'name': 'News', 'alias': 'news'},
    'navigation': {'name': 'Navigation', 'alias': 'navigation'},
}

```

## Using
Lets see on your `APP_BLOG_PAGE_TYPES` config:
Each page type have attributes
- type id - `navigation` in example above. Must be unique
- type name - `Navigation` in example above
- alias - `navigation`, for example

If you leave alias empty, ...