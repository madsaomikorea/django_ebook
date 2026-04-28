import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from schools.models import Subject

common_subjects = ["O'zbek tili", "Adabiyot", "Matematika", "Informatika", "Fizika", "Kimyo", "Biologiya", "Tarix", "Ingliz tili", "Rus tili", "Jismoniy tarbiya", "Geografiya", "Iqtisod", "Huquq"]

for name in common_subjects:
    Subject.objects.get_or_create(name=name)

print("Subjects populated!")
