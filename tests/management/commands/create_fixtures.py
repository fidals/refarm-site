"""Create serialized data for tests and store this data in a json file."""
import abc
import typing

from django.core.management import call_command
from django.core.management.base import BaseCommand

from tests.catalog import models as catalog_models


class GeneratedFixture(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def generate(self):
        """Generate fixture for tests."""


class GeneratedFixtures(GeneratedFixture):

    def __init__(self, *fixtures: typing.List[GeneratedFixture]):
        self.fixtures = fixtures

    def generate(self):
        for fixture in self.fixtures:
            fixture.generate()


class GeneratedToFile(GeneratedFixture):

    def __init__(
        self,
        fixture: GeneratedFixture,
        file_name: str,
        apps: typing.List[str],
    ):
        self.apps = apps
        self.fixture = fixture
        self.file_name = file_name

    def generate(self):
        call_command('flush', '--noinput')
        self.fixture.generate()
        call_command(
            'dumpdata',
            *self.apps,
            output=f'tests/fixtures/{self.file_name}'
        )


class GeneratedCatalog(GeneratedFixture):

    def __init__(
        self,
        categories_data: typing.List[dict],
        products_data: typing.List[dict],
    ):
        self.categories_data = categories_data
        self.products_data = products_data

    def generate(self):
        for category_data in self.categories_data:
            category = catalog_models.MockCategory.objects.create(**category_data)
            for product_data in self.products_data:
                catalog_models.MockProduct.objects.create(
                    category=category, **product_data,
                )


class GeneratedPages(GeneratedFixture):

    def generate(self):
        call_command('custom_pages')


# @todo #230:120m Create base class for `create_fixtures`.
#  And use it for refarm and every site.
#  Sites now call it `test_db` instead `create_fixtures`.
class Command(BaseCommand):

    # @todo #230:120m Use fixtures in every test.
    def handle(self, *args, **options):
        call_command('migrate')

        categories_data = [{'name': 'Batteries'}]
        products_data = [
            {'name': f'{product_name} for {name}'}
            for product_name in ['Battery', 'USB', 'Charger', 'Accumulator']
            for name in ['Alice', 'Bob', 'Eve', 'Dave']
        ]

        GeneratedToFile(
            fixture=GeneratedFixtures(
                GeneratedCatalog(
                    categories_data=categories_data,
                    products_data=products_data,
                ),
                GeneratedPages(),
            ),
            apps=['pages', 'tests', 'mptt'],
            file_name='catalog.json',
        ).generate()
