from django.core.management.base import BaseCommand
from scripts.seed_large import seed

class Command(BaseCommand):
    help = 'Populate the database with large amount of demo data (Karakalpakstan schools, students, books, etc.)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))
        try:
            seed()
            self.stdout.write(self.style.SUCCESS('Data seeding completed successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))
