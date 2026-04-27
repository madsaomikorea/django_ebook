import os
import django
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import CustomUser

def setup_superuser():
    username = 'admin'
    password = 'superadmin'
    
    user, created = CustomUser.objects.get_or_create(username=username)
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.role = 'superuser'
    user.save()
    
    if created:
        print(f"Superuser '{username}' created with password '{password}'")
    else:
        print(f"Superuser '{username}' updated with password '{password}'")

if __name__ == '__main__':
    setup_superuser()
