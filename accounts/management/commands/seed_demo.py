from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from schools.models import School

class Command(BaseCommand):
    help = 'Seeds the database with demo users'

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

        # 3. Create School Admin
        if not CustomUser.objects.filter(username='school_admin').exists():
            CustomUser.objects.create_user(
                username='school_admin',
                email='school@demo.com',
                password='password123',
                role='school_admin',
                school=school
            )
            self.stdout.write(self.style.SUCCESS('School Admin created: school_admin / password123'))

        # 4. Create Teacher
        if not CustomUser.objects.filter(username='teacher_demo').exists():
            CustomUser.objects.create_user(
                username='teacher_demo',
                email='teacher@demo.com',
                password='password123',
                role='teacher',
                school=school
            )
            self.stdout.write(self.style.SUCCESS('Teacher created: teacher_demo / password123'))

        # 5. Create Student
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
