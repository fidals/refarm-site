"""Create serialized data for tests and store this data in a json file."""
import os
from contextlib import contextmanager

from django.core.management import call_command
from django.core.management.base import BaseCommand

from pages.models import CustomPage
from tests.catalog import models as catalog_models


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.prepare_db()
        with self.save_to('search.json'):
            self.create_custom_pages()
            self.create_for_search()

    def prepare_db(self):
        call_command('migrate')

    @contextmanager
    def save_to(self, name: str):
        """Save .json dump to fixtures."""
        call_command('flush', '--noinput')
        yield
        call_command(
            'dumpdata',
            'pages', 'tests', 'mptt',
            output=f'tests/fixtures/{name}'
        )

    def create_custom_pages(self):
        CustomPage.objects.create(slug='search')
        CustomPage.objects.create(slug='catalog')

    def create_for_search(self):
        test_category_first = catalog_models.MockCategory.objects.create(
            name='Batteries',
        )

        for product in ['Battery', 'USB']:
            for name in ['Alice', 'Bob']:
                catalog_models.MockProduct.objects.create(
                    name=f'{product} for {name}',
                    category=test_category_first,
                )

