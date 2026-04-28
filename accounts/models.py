from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('superuser', _('Superuser')),
        ('school_admin', _('School Admin')),
        ('student', _('Student')),
        ('teacher', _('Teacher')),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    school = models.ForeignKey('schools.School', on_delete=models.SET_NULL, null=True, blank=True)
    grade = models.CharField(max_length=10, null=True, blank=True)  # класс для ученика
    subject = models.CharField(max_length=100, null=True, blank=True) # предмет для учителя
    birth_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    raw_password = models.CharField(max_length=128, null=True, blank=True) # Для суперадмина

    def save(self, *args, **kwargs):
        if self.is_superuser and self.role != 'superuser':
            self.role = 'superuser'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
