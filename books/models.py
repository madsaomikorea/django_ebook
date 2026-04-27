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

    @property
    def currently_reading_count(self):
        return self.total_count - self.available_count

    def save(self, *args, **kwargs):
        # Image optimization: resize and compress cover only if it's new or changed
        if self.cover:
            try:
                # Check if this is a new file being uploaded
                # (it won't have a value in _committed if it's a new UploadedFile)
                is_new_image = not getattr(self.cover, '_committed', True)
                
                if is_new_image:
                    from PIL import Image
                    from io import BytesIO
                    from django.core.files.base import ContentFile
                    import os

                    img = Image.open(self.cover)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    MAX_SIZE = (800, 1200)
                    if img.height > MAX_SIZE[1] or img.width > MAX_SIZE[0]:
                        img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
                    
                    buffer = BytesIO()
                    img.save(buffer, format='JPEG', quality=75, optimize=True)
                    
                    filename = os.path.basename(self.cover.name)
                    # Use a unique name if necessary, but here we just want to avoid 
                    # the infinite loop/duplicate issue on every model save
                    self.cover.save(filename, ContentFile(buffer.getvalue()), save=False)
            except Exception as e:
                print(f"Error optimizing image: {e}")
                
        super().save(*args, **kwargs)

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
