=====
Blog
=====

.. image:: https://travis-ci.org/fidals/refarm-blog.svg?branch=master
    :target: https://travis-ci.org/fidals/refarm-blog

Provides basic blog functionality to your Django project.



Quick start
-----------

1. Install the refarm-blog app in your Django project

`pip install -e git://github.com/fidals/refarm-blog.git#egg=refarm-blog`


2. Add blog app to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'blog',
    ]

3. Set APP_BLOG_POST_TYPES to your settings.py. Example::

APP_BLOG_POST_TYPES = {
    'article': {'name': 'Weekly articles', 'alias': ''},
    'news': {'name': 'My news', 'alias': 'news'},
    'navigation': {'name': 'Site navigation', 'alias': 'navigation'},
}

4. Include the blog URLconf in your project urls.py like this::

    url(r'^blog/', include('blog.urls')),

5. Run `python manage.py migrate` apply migrations

6. Add some models via admin dashboard

7. Visit http://127.0.0.1:8000/blog/ to view pages list


Define your posts types
-----
Lets see `APP_BLOG_POST_TYPES` config:
Each page type have attributes
- type id - `navigation` in example above. Must be unique
- type name - `Navigation` in example above
- alias - `navigation`, for example

Now, you have following urls:
`/blog/[alias]/[id]`

If you leave alias empty, urls will be like this:
`/blog/[id]`
