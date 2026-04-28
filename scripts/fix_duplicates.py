import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from schools.models import School

def fix_duplicates():
    names = School.objects.values_list('name', flat=True)
    duplicates = [name for name in set(names) if list(names).count(name) > 1]
    
    if not duplicates:
        print("No duplicate school names found.")
        return

    print(f"Found duplicates: {duplicates}")
    for name in duplicates:
        schools = School.objects.filter(name=name).order_by('id')
        # Keep the first one, rename others
        for i, school in enumerate(schools[1:], start=2):
            new_name = f"{school.name} ({i})"
            print(f"Renaming {school.name} (ID: {school.id}) to {new_name}")
            school.name = new_name
            school.save()

if __name__ == "__main__":
    fix_duplicates()
