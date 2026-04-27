import os
import sys
import django

sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import CustomUser

username = 'teacher_user'
password = 'teacher123'

try:
    user = CustomUser.objects.get(username=username)
    user.set_password(password)
    user.save()
    print(f"Password for '{username}' has been reset to '{password}'.")
except CustomUser.DoesNotExist:
    # If not exists, create one
    user = CustomUser.objects.create_user(
        username=username,
        password=password,
        role='teacher',
        first_name='Test',
        last_name='Teacher'
    )
    print(f"Teacher account '{username}' created with password '{password}'.")
