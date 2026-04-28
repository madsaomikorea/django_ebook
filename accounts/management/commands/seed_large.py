from django.core.management.base import BaseCommand
import random
from datetime import timedelta
from django.utils import timezone
from schools.models import School, District, Subject, Institution
from books.models import Book, Category, BookIssue, BookRequest
from frontend_school.models import News
from accounts.models import CustomUser

class Command(BaseCommand):
    help = 'Seeds the database with a large amount of Karakalpakstan demo data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Delete existing data before seeding',
        )

    def handle(self, *args, **options):
        # Check if data already exists
        if School.objects.exists() and not options['force']:
            self.stdout.write(self.style.SUCCESS("Data already exists. Skipping seed. Use --force to re-seed."))
            return

        if options['force']:
            self.stdout.write(self.style.WARNING("Clearing existing data..."))
            Book.objects.all().delete()
            School.objects.all().delete()
            District.objects.all().delete()
            Institution.objects.all().delete()
            CustomUser.objects.filter(is_superuser=False).delete()

        # 1. Create Superuser if doesn't exist
        if not CustomUser.objects.filter(username='admin').exists():
            CustomUser.objects.create_superuser(
                username='admin',
                email='admin@demo.com',
                password='superadmin',
                role='superuser'
            )
            self.stdout.write(self.style.SUCCESS('Superuser created: admin / superadmin'))

        self.stdout.write("Starting Karakalpakstan data seeding...")

        # 1. Create Districts
        districts_names = [
            "Nukus shahri", "Amudaryo tumani", "Beruniy tumani", "Chimboy tumani", 
            "Ellikqala tumani", "Kegeyli tumani", "Mo'ynoq tumani", "Nukus tumani"
        ]
        districts = []
        for name in districts_names:
            d, _ = District.objects.get_or_create(name=name)
            districts.append(d)

        subjects_names = ["Matematika", "Fizika", "Kimyo", "Informatika", "O'zbek tili", "Ingliz tili"]
        subjects = [Subject.objects.get_or_create(name=name)[0] for name in subjects_names]

        categories_names = ["Badiiy adabiyot", "Ilmiy-ommabop", "Darslik", "Tarix"]
        categories = [Category.objects.get_or_create(name=name)[0] for name in categories_names]

        first_names = ["Anvar", "Baxit", "Daulet", "Erkin", "Farhod", "Gulmira", "Inju", "Jalgas"]
        last_names = ["Kidirbaev", "Embergenov", "Dauletov", "Saparov", "Ametov"]
        book_titles = ["O'tkan kunlar", "Mehrobdan chayon", "Shum bola", "Yulduzli tunlar", "Kichik shahzoda"]

        all_books_to_create = []

        def clean_name(name):
            return "".join(c for c in name.lower() if c.isalnum() or c == '_').strip('_')

        for d_idx, district in enumerate(districts):
            # 1-2 schools per district
            num_schools = 1 if d_idx > 0 else 2 
            for s_idx in range(1, num_schools + 1): 
                school_name = f"{district.name} {s_idx}-sonli maktab"
                school = School.objects.create(
                    name=school_name,
                    address=f"{district.name}, Markaz",
                    contact=f"+99861222{random.randint(1000, 9999)}",
                    district=district
                )
                
                district_part = clean_name(school.district.name if school.district else "no")
                school_part = clean_name(school.name)

                # School Admin
                admin = CustomUser.objects.create_user(
                    username=f"temp_adm_{d_idx}_{s_idx}", 
                    password="password123", 
                    role="school_admin", 
                    school=school,
                    first_name=random.choice(first_names),
                    last_name=random.choice(last_names)
                )
                admin.username = f"{district_part}_{school_part}_adm_{admin.id}"
                admin.raw_password = 'password123'
                admin.save()

                # Teachers
                for t in range(2):
                    teacher = CustomUser.objects.create_user(
                        username=f"temp_t_{d_idx}_{s_idx}_{t}",
                        password="password123",
                        role="teacher",
                        school=school,
                        first_name=random.choice(first_names),
                        last_name=random.choice(last_names),
                        subject=random.choice(subjects).name
                    )
                    teacher.username = f"{district_part}_{school_part}_{teacher.id}"
                    teacher.raw_password = 'password123'
                    teacher.save()

                # Students
                for st in range(5):
                    student = CustomUser.objects.create_user(
                        username=f"temp_st_{d_idx}_{s_idx}_{st}",
                        password="password123",
                        role="student",
                        school=school,
                        first_name=random.choice(first_names),
                        last_name=random.choice(last_names),
                        grade="9-A"
                    )
                    student.username = f"{district_part}_{school_part}_{student.id}"
                    student.raw_password = 'password123'
                    student.save()

                # Books
                for b in range(15):
                    all_books_to_create.append(Book(
                        school=school,
                        title=f"{random.choice(book_titles)} {random.randint(1, 100)}",
                        description="Demo book description.",
                        category=random.choice(categories),
                        total_count=10,
                        available_count=10,
                        borrow_count=random.randint(0, 10)
                    ))

        Book.objects.bulk_create(all_books_to_create)
        self.stdout.write(self.style.SUCCESS(f'Seed successful! Password for all: password123'))

