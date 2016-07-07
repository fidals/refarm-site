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
        'pages',
    ]

3. Include the blog URLconf in your project urls.py like this::

    url(r'^blog/', include('blog.urls')),

4. Run `python manage.py migrate` apply migrations

5. Add some models via admin dashboard

6. Visit http://127.0.0.1:8000/blog/ to view pages list
