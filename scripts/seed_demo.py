import os
import sys
import django

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from schools.models import School
from books.models import Book, Category
from accounts.models import CustomUser

def seed():
    # Create Schools
    s1 = School.objects.create(name="Toshkent 1-sonli maktab", address="Toshkent sh., Yunusobod", contact="+998901234567")
    s2 = School.objects.create(name="Samarqand 12-sonli maktab", address="Samarqand sh., Registon", contact="+998912345678")
    
    # Create Categories
    c1 = Category.objects.create(name="Badiiy adabiyot")
    c2 = Category.objects.create(name="Ilmiy-ommabop")
    
    # Create Books
    Book.objects.create(
        school=s1, title="O'tkan kunlar", description="Abdulla Qodiriyning shoh asari.", 
        category=c1, total_count=10, available_count=8, borrow_count=25
    )
    Book.objects.create(
        school=s1, title="Mehrobdan chayon", description="Tarixiy roman.", 
        category=c1, total_count=5, available_count=5, borrow_count=12
    )
    Book.objects.create(
        school=s2, title="Fizika asoslari", description="Maktab darsligi.", 
        category=c2, total_count=20, available_count=20, borrow_count=5
    )
    
    # Create School Admin
    admin_user = CustomUser.objects.create_user(username="school_admin", password="password123", role="school_admin", school=s1)
    
    # Create Student
    student_user = CustomUser.objects.create_user(username="student_user", password="password123", role="student", school=s1)

    print("Demo data seeded successfully!")

if __name__ == '__main__':
    seed()
