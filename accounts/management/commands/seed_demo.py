from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from schools.models import School
from books.models import Category, Book

class Command(BaseCommand):
    help = 'Seeds the database with demo users and books'

    def handle(self, *args, **kwargs):
        # 1. Create Superuser
        if not CustomUser.objects.filter(username='admin').exists():
            CustomUser.objects.create_superuser(
                username='admin',
                email='admin@demo.com',
                password='superadmin',
                role='superuser'
            )
            self.stdout.write(self.style.SUCCESS('Superuser created: admin / superadmin'))

        # 2. Create Demo School
        school, created = School.objects.get_or_create(
            name='Demo School #1',
            defaults={'address': 'Demo Street 123', 'contact': '+998901234567'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'School created: {school.name}'))

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
                'title': 'Oʻtgan kunlar',
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
        if not CustomUser.objects.filter(username='school_admin').exists():
            CustomUser.objects.create_user(
                username='school_admin',
                email='school@demo.com',
                password='password123',
                role='school_admin',
                school=school
            )
            self.stdout.write(self.style.SUCCESS('School Admin created: school_admin / password123'))

        # 6. Create Teacher
        if not CustomUser.objects.filter(username='teacher_demo').exists():
            CustomUser.objects.create_user(
                username='teacher_demo',
                email='teacher@demo.com',
                password='password123',
                role='teacher',
                school=school
            )
            self.stdout.write(self.style.SUCCESS('Teacher created: teacher_demo / password123'))

        # 7. Create Student
        if not CustomUser.objects.filter(username='student_demo').exists():
            CustomUser.objects.create_user(
                username='student_demo',
                email='student@demo.com',
                password='password123',
                role='student',
                school=school,
                grade='9-A'
            )
            self.stdout.write(self.style.SUCCESS('Student created: student_demo / password123'))

        self.stdout.write(self.style.SUCCESS('Demo seeding completed successfully!'))
