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

        # 1. Create Districts (Karakalpakstan)
        districts_names = [
            "Nukus shahri", "Amudaryo tumani", "Beruniy tumani", "Chimboy tumani", 
            "Ellikqala tumani", "Kegeyli tumani", "Mo'ynoq tumani", "Nukus tumani", 
            "Qonliko'l tumani", "Qorao'zak tumani", "Qo'ng'irot tumani", "Shumanay tumani", 
            "Taxtako'pir tumani", "To'rtko'l tumani", "Xo'jayli tumani", "Taxiatosh tumani", 
            "Bo'zatov tumani"
        ]
        districts = []
        for name in districts_names:
            d, _ = District.objects.get_or_create(name=name)
            districts.append(d)

        # 2. Create Subjects
        subjects_names = ["Matematika", "Fizika", "Kimyo", "Informatika", "O'zbek tili", "Ingliz tili"]
        subjects = []
        for name in subjects_names:
            s, _ = Subject.objects.get_or_create(name=name)
            subjects.append(s)

        # 3. Create Categories
        categories_names = ["Badiiy adabiyot", "Ilmiy-ommabop", "Darslik", "Tarix"]
        categories = []
        for name in categories_names:
            c, _ = Category.objects.get_or_create(name=name)
            categories.append(c)

        # 4. Create Schools and Users
        first_names = ["Anvar", "Baxit", "Daulet", "Erkin", "Farhod", "Gulmira", "Inju", "Jalgas"]
        last_names = ["Kidirbaev", "Embergenov", "Dauletov", "Saparov", "Ametov"]

        book_titles = ["O'tkan kunlar", "Mehrobdan chayon", "Shum bola", "Yulduzli tunlar", "Kichik shahzoda"]

        all_books_to_create = []

        # Reduce number of districts/schools for automatic seed to prevent timeout
        # We'll seed 5 districts for the automatic run
        active_districts = districts[:8] 

        for d_idx, district in enumerate(active_districts):
            num_schools = 1 if d_idx > 0 else 2 
            for i in range(1, num_schools + 1): 
                school_name = f"{district.name.replace(' shahri', '').replace(' tumani', '')} {i}-sonli maktab"
                school = School.objects.create(
                    name=school_name,
                    address=f"{district.name}, Markaz",
                    contact=f"+99861222{random.randint(1000, 9999)}",
                    district=district
                )
                
                # School Admin
                admin_username = f"admin_{district.id}_{i}"
                if not CustomUser.objects.filter(username=admin_username).exists():
                    CustomUser.objects.create_user(
                        username=admin_username, 
                        password="password123", 
                        role="school_admin", 
                        school=school,
                        first_name=random.choice(first_names),
                        last_name=random.choice(last_names)
                    )

                # Teachers (Reduced to 2 per school)
                for t in range(2):
                    t_username = f"teacher_{district.id}_{i}_{t}"
                    if not CustomUser.objects.filter(username=t_username).exists():
                        CustomUser.objects.create_user(
                            username=t_username,
                            password="password123",
                            role="teacher",
                            school=school,
                            first_name=random.choice(first_names),
                            last_name=random.choice(last_names),
                            subject=random.choice(subjects).name
                        )

                # Students (Reduced to 5 per school)
                for s in range(5):
                    s_username = f"student_{district.id}_{i}_{s}"
                    if not CustomUser.objects.filter(username=s_username).exists():
                        CustomUser.objects.create_user(
                            username=s_username,
                            password="password123",
                            role="student",
                            school=school,
                            first_name=random.choice(first_names),
                            last_name=random.choice(last_names),
                            grade="9-A"
                        )

                # Collect books for bulk create
                for b in range(20):
                    all_books_to_create.append(Book(
                        school=school,
                        title=f"{random.choice(book_titles)} {random.randint(1, 100)}",
                        description="Demo book description.",
                        category=random.choice(categories),
                        total_count=10,
                        available_count=10,
                        borrow_count=random.randint(0, 10)
                    ))

        # Bulk create books
        Book.objects.bulk_create(all_books_to_create)

        self.stdout.write(self.style.SUCCESS('Karakalpakstan data seeding completed successfully!'))
