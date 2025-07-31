from django.core.management.base import BaseCommand
from django.urls import get_resolver

class Command(BaseCommand):
    help = 'Display all URLs in the project'

    def handle(self, *args, **options):
        resolver = get_resolver()
        for url_pattern in resolver.url_patterns:
            self.stdout.write(self.style.SUCCESS(f'URL: {url_pattern.pattern}'))
            if hasattr(url_pattern, 'url_patterns'):
                for sub_pattern in url_pattern.url_patterns:
                    self.stdout.write(self.style.SUCCESS(f'  - {sub_pattern.pattern}'))