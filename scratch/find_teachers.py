import os
import sys
import django

sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import CustomUser

teachers = CustomUser.objects.filter(role='teacher')
for t in teachers:
    print(f"Username: {t.username}, Name: {t.first_name} {t.last_name}")

if not teachers:
    print("No teachers found. Listing some users:")
    for u in CustomUser.objects.all()[:10]:
        print(f"Username: {u.username}, Role: {u.role}")
