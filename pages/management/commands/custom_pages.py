from django.core.management.base import BaseCommand
from pages.utils import save_custom_pages


class Command(BaseCommand):
    def handle(self, *args, **options):
        save_custom_pages()
