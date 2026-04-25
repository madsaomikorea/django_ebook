from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Book(models.Model):
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    cover = models.ImageField(upload_to='book_covers/%Y/%m/%d/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    total_count = models.IntegerField()
    available_count = models.IntegerField()
    borrow_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class BookIssue(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    return_qr_code = models.ImageField(upload_to='return_qrs/%Y/%m/%d/', null=True, blank=True)
    qr_token = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.book.title} -> {self.user.username}"

class BookRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Kutilmoqda'),
        ('approved', 'Tasdiqlandi'),
        ('rejected', 'Rad etildi'),
        ('completed', 'Yakunlandi'),
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    qr_code = models.ImageField(upload_to='request_qrs/%Y/%m/%d/', null=True, blank=True)
    qr_token = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Request: {self.book.title} by {self.user.username}"
