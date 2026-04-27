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
        self.stdout.write(f"Created {len(districts)} districts.")

        # 2. Create Subjects
        subjects_names = [
            "Matematika", "Fizika", "Kimyo", "Biologiya", "Informatika", 
            "O'zbek tili", "Qoraqalpoq tili", "Rus tili", "Ingliz tili", "Tarix", 
            "Geografiya", "Adabiyot", "Tasviriy san'at", "Musiqa", "Jismoniy tarbiya"
        ]
        subjects = []
        for name in subjects_names:
            s, _ = Subject.objects.get_or_create(name=name)
            subjects.append(s)

        # 3. Create Categories
        categories_names = [
            "Badiiy adabiyot", "Ilmiy-ommabop", "Tarixiy", "Darslik", 
            "Xorijiy tillar", "Psixologiya", "Bolalar adabiyoti", "Detektiv"
        ]
        categories = []
        for name in categories_names:
            c, _ = Category.objects.get_or_create(name=name)
            categories.append(c)

        # 4. Create Schools and Users
        first_names = ["Anvar", "Baxit", "Daulet", "Erkin", "Farhod", "Gulmira", "Inju", "Jalgas", "Kuanish", "Madiyar", "Nurbek", "Oydin", "Polat", "Qural"]
        last_names = ["Kidirbaev", "Embergenov", "Dauletov", "Saparov", "Jumanazarov", "Oralbaev", "Tadjibaev", "Mamutov", "Begjanov", "Ametov"]

        book_titles = [
            "O'tkan kunlar", "Mehrobdan chayon", "Sariq devni minib", "Shum bola", 
            "Ufq", "Ikki eshik orasi", "Dunyoning ishlari", "Yulduzli tunlar", 
            "Avlodlar dovoni", "Kecha va kunduz", "Navoiy", "Jimjitlik", 
            "Sohibqiron", "Temur tuzuklari", "Al-Kimyogar", "1984", 
            "Kichik shahzoda", "Sherlok Xolms", "Garri Potter", "Raqamli qal'a",
            "Boy ota, kambag'al ota", "Muvaffaqiyat kaliti", "O'z-o'ziga yordam",
            "Fizika 7-sinf", "Algebra 8-sinf", "Kimyo 9-sinf", "Ingliz tili darsligi"
        ]

        for d_idx, district in enumerate(districts):
            # 2 schools per district
            num_schools = 2 if d_idx > 0 else 3 
            for i in range(1, num_schools + 1): 
                school_name = f"{district.name.replace(' shahri', '').replace(' tumani', '')} {i}-sonli maktab"
                school = School.objects.create(
                    name=school_name,
                    address=f"{district.name}, Markaziy ko'chasi, {random.randint(1, 150)}-uy",
                    contact=f"+99861{random.randint(222, 999)}{random.randint(1000, 9999)}",
                    district=district
                )
                
                # School Admin
                admin_username = f"admin_{d_idx}_{i}"
                CustomUser.objects.create_user(
                    username=admin_username, 
                    password="password123", 
                    role="school_admin", 
                    school=school,
                    first_name=random.choice(first_names),
                    last_name=random.choice(last_names)
                )

                # Teachers
                for t in range(5): # Reduced for faster seeding but still plenty
                    t_username = f"teacher_{d_idx}_{i}_{t}"
                    CustomUser.objects.create_user(
                        username=t_username,
                        password="password123",
                        role="teacher",
                        school=school,
                        first_name=random.choice(first_names),
                        last_name=random.choice(last_names),
                        subject=random.choice(subjects).name
                    )

                # Students
                grades = ["7-A", "7-B", "8-A", "8-B", "9-A", "9-V", "10-A", "11-B"]
                students = []
                for s in range(20): # Reduced count for automated deployment safety
                    s_username = f"student_{d_idx}_{i}_{s}"
                    student = CustomUser.objects.create_user(
                        username=s_username,
                        password="password123",
                        role="student",
                        school=school,
                        first_name=random.choice(first_names),
                        last_name=random.choice(last_names),
                        grade=random.choice(grades)
                    )
                    students.append(student)

                # Books
                books = []
                for b in range(50): # Reduced for speed
                    title = f"{random.choice(book_titles)} {random.randint(1, 1000)}" if b > len(book_titles) else book_titles[b % len(book_titles)]
                    total = random.randint(10, 100)
                    book = Book.objects.create(
                        school=school,
                        title=title,
                        description=f"Bu '{title}' kitobi haqida qisqacha ma'lumot.",
                        category=random.choice(categories),
                        total_count=total,
                        available_count=total,
                        borrow_count=random.randint(0, 100)
                    )
                    books.append(book)

        # 5. Institutions
        kk_institutions = [
            "Qoraqalpoq davlat universiteti",
            "Nukus davlat pedagogika instituti",
            "Toshkent tibbiyot akademiyasi Nukus filiali"
        ]
        for name in kk_institutions:
            Institution.objects.get_or_create(name=name, defaults={'address': "Nukus shahri, Markaz"})

        self.stdout.write(self.style.SUCCESS('Karakalpakstan data seeding completed successfully!'))
