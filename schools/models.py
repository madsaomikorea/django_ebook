from django.db import models

class District(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class School(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='schools')

    def __str__(self):
        return self.name

class Institution(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
