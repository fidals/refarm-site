import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='refarm-site',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',  # example license
    description='Provides base site pages functionality to your Django project.',
    long_description=README,
    url='https://github.com/fidals/refarm-site',
    author='Duker33',
    author_email='info@fidals.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'celery==4.1.1',
        'Django==1.11.17',  # python 3.7 compatible
        'django-mptt==0.8.7',
        'dj-database-url==0.4.1',
        'sorl-thumbnail==12.4a1',
        'Django-Select2==5.11.1',
        'unidecode',
        'psycopg2-binary==2.7.5',
        'Pillow==5.2.0',
    ],
)
