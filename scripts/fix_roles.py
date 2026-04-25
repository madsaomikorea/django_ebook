import os
import sys
import django

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import CustomUser

# Fix all superusers to have 'superuser' role
superusers = CustomUser.objects.filter(is_superuser=True)
updated_count = superusers.update(role='superuser')
print(f"Updated {updated_count} superusers to have 'superuser' role.")

# Fix 'admin' specifically if it's not a superuser but named admin
admin_user = CustomUser.objects.filter(username='admin').first()
if admin_user and admin_user.role == 'student':
    admin_user.role = 'superuser'
    admin_user.save()
    print("Updated 'admin' user role to 'superuser'.")
