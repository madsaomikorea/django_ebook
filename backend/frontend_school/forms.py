from django import forms
from django.utils.translation import gettext_lazy as _
from books.models import Book
from accounts.models import CustomUser
from .models import News

class BookForm(forms.ModelForm):
    category_name = forms.CharField(
        required=False,
        label=_("Kategoriya"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'list': 'category-list', 'autocomplete': 'off'})
    )

    class Meta:
        model = Book
        fields = ['title', 'description', 'cover', 'total_count', 'available_count']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'total_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_count': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from books.models import Category
        # Set initial value for category name if editing
        if self.instance and self.instance.category:
            self.fields['category_name'].initial = self.instance.category.name
        
        # Add categories for datalist
        self.categories = Category.objects.all().order_by('name')

    def save(self, commit=True):
        from books.models import Category
        category_name = self.cleaned_data.get('category_name')
        book = super().save(commit=False)
        
        if category_name:
            category, created = Category.objects.get_or_create(name=category_name)
            book.category = category
        else:
            book.category = None
            
        if commit:
            book.save()
        return book

class StudentForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'grade', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'grade': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.utils.translation import gettext_lazy as _
        self.fields['username'].label = _("Foydalanuvchi nomi")
        self.fields['first_name'].label = _("Ism")
        self.fields['last_name'].label = _("Familiya")
        self.fields['grade'].label = _("Sinf")
        self.fields['password'].label = _("Parol")

class TeacherForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.utils.translation import gettext_lazy as _
        self.fields['username'].label = _("Foydalanuvchi nomi")
        self.fields['first_name'].label = _("Ism")
        self.fields['last_name'].label = _("Familiya")
        self.fields['password'].label = _("Parol")

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'body', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
