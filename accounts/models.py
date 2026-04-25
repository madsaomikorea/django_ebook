from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('superuser', 'Superuser'),
        ('school_admin', 'School Admin'),
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    school = models.ForeignKey('schools.School', on_delete=models.SET_NULL, null=True, blank=True)
    grade = models.CharField(max_length=10, null=True, blank=True)  # класс для ученика

    def save(self, *args, **kwargs):
        if self.is_superuser and self.role != 'superuser':
            self.role = 'superuser'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
