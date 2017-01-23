.. image:: https://travis-ci.org/fidals/refarm-site.svg?branch=master
    :target: https://travis-ci.org/fidals/refarm-site


=====
Pages
=====

Provides basic pages functionality to your Django project.

Quick start
-----------


1. Install the refarm-site app in your Django project

`pip install -e git://github.com/fidals/refarm-site.git#egg=refarm-site`


2. Add pages app to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'pages',
    ]

3. Include the pages URLconf in your project urls.py like this::

    url(r'^pages/', include('pages.urls')),

4. Run `python manage.py migrate` to apply migrations.

5. Visit http://127.0.0.1:8000/pages/ to view pages list


=====
eCommerce
=====

eCommerce is a simple Django app which provides basic functionality for a typical e-commerce shop.


Quick start
-----------

1. Add "ecommerce" to your INSTALLED_APPS setting like this:

    INSTALLED_APPS = [
        ...
        'ecommerce',
    ]

2. Include the eCommerce URLconf in your project urls.py like this:

    url(r'^shop/', include('ecommerce.urls')),

3. Define constants in your `settings.py`:

    CART_ID = 'cart' # key for storing cart's object in user session

    PRODUCT_MODEL = 'catalog.Product' # model which should be stored in cart

    SEND_MAIL = True # Would you like to send mails with order information? NOTE: You must have working SMTP

    SHOP_EMAIL = 'your@amazing.shop' # From this email letters will be sent.

3. Run ``python manage.py makemigrations ecommerce`` to create migrations.

4. ``python manage.py migrate`` to apply them.

5. Now you can use eCommerce app in your project.


=====
Catalog
=====

Catalog is a simple Django app which provides basic functionality for a typical e-commerce catalog.


Quick start
-----------

1. Add "catalog" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'catalog',
    ]

2. Include the catalog URLconf in your project urls.py like this::

    url(r'^catalog/', include('catalog.urls')),

3. Run `python manage.py migrate`

4. Visit http://127.0.0.1:8000/catalog/ to view category tree
