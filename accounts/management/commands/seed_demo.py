from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from schools.models import School
from books.models import Category, Book

class Command(BaseCommand):
    help = 'Seeds the database with demo users and books'

    def handle(self, *args, **kwargs):
        def clean_name(name):
            return "".join(c for c in name.lower() if c.isalnum() or c == '_').strip('_')

        # 1. Create Superuser
        if not CustomUser.objects.filter(username='admin').exists():
            CustomUser.objects.create_superuser(
                username='admin',
                email='admin@demo.com',
                password='superadmin',
                role='superuser'
            )
            self.stdout.write(self.style.SUCCESS('Superuser created: admin / superadmin'))

        # 1.1 Create Demo District
        from schools.models import District
        district, _ = District.objects.get_or_create(name='Nukus shahri')

        # 2. Create Demo School
        school, created = School.objects.get_or_create(
            name='Demo School #1',
            defaults={
                'address': 'Demo Street 123', 
                'contact': '+998901234567',
                'district': district
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'School created: {school.name}'))

        district_part = clean_name(school.district.name if school.district else "no")
        school_part = clean_name(school.name)

        # 3. Create Categories
        categories = ['Badiiy adabiyot', 'Ilmiy-ommabop', 'Darsliklar', 'Tarix']
        cat_objects = {}
        for cat_name in categories:
            cat, created = Category.objects.get_or_create(name=cat_name)
            cat_objects[cat_name] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f'Category created: {cat_name}'))

        # 4. Create Demo Books
        demo_books = [
            {
                'title': "O'tgan kunlar",
                'description': 'Abdulla Qodiriyning eng mashhur asari.',
                'category': cat_objects['Badiiy adabiyot'],
                'total_count': 10,
                'available_count': 10
            },
            {
                'title': 'Stiv Jobs',
                'description': 'Uolter Ayzekson qalamiga mansub biografiya.',
                'category': cat_objects['Ilmiy-ommabop'],
                'total_count': 5,
                'available_count': 5
            },
            {
                'title': 'Matematika 9-sinf',
                'description': 'Oʻrta maktab darsligi.',
                'category': cat_objects['Darsliklar'],
                'total_count': 30,
                'available_count': 30
            }
        ]

        for book_data in demo_books:
            book, created = Book.objects.get_or_create(
                title=book_data['title'],
                school=school,
                defaults={
                    'description': book_data['description'],
                    'category': book_data['category'],
                    'total_count': book_data['total_count'],
                    'available_count': book_data['available_count']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Book created: {book.title}"))

        # 5. Create School Admin
        if not CustomUser.objects.filter(role='school_admin', school=school).exists():
            admin = CustomUser.objects.create_user(
                username='temp_adm',
                password='password123',
                role='school_admin',
                school=school,
                first_name='Ali',
                last_name='Valiyev'
            )
            admin.username = f"{district_part}_{school_part}_adm_{admin.id}"
            admin.raw_password = 'password123'
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'School Admin created: {admin.username} / password123'))

        # 6. Create Teacher
        if not CustomUser.objects.filter(role='teacher', school=school).exists():
            teacher = CustomUser.objects.create_user(
                username='temp_teacher',
                password='password123',
                role='teacher',
                school=school,
                first_name='Zuhra',
                last_name='Aliyeva',
                subject='Matematika'
            )
            teacher.username = f"{district_part}_{school_part}_{teacher.id}"
            teacher.raw_password = 'password123'
            teacher.save()
            self.stdout.write(self.style.SUCCESS(f'Teacher created: {teacher.username} / password123'))

        # 7. Create Student
        if not CustomUser.objects.filter(role='student', school=school).exists():
            student = CustomUser.objects.create_user(
                username='temp_student',
                password='password123',
                role='student',
                school=school,
                first_name='Umar',
                last_name='Hasanov',
                grade='9-A'
            )
            student.username = f"{district_part}_{school_part}_{student.id}"
            student.raw_password = 'password123'
            student.save()
            self.stdout.write(self.style.SUCCESS(f'Student created: {student.username} / password123'))

        self.stdout.write(self.style.SUCCESS('Demo seeding completed successfully!'))

