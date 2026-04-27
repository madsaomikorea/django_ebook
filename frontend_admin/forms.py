from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from schools.models import School, Institution, District

def validate_word_limit(value, limit):
    if not value: return
    words = value.split()
    if len(words) > limit:
        raise ValidationError(_(f"Limit: {limit} ta so'z. Siz {len(words)} ta so'z kiritdingiz."))

def validate_char_limit(value, limit):
    if not value: return
    if len(value) > limit:
        raise ValidationError(_(f"Limit: {limit} ta belgi. Siz {len(value)} ta belgi kiritdingiz."))

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ['district', 'name', 'address', 'contact']
        widgets = {
            'district': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'data-limit-chars': '150'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'data-limit-chars': '255'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'data-limit-chars': '100'}),
        }
    def clean_name(self):
        name = self.cleaned_data.get('name')
        validate_char_limit(name, 150)
        return name
    def clean_address(self):
        val = self.cleaned_data.get('address')
        validate_char_limit(val, 255)
        return val
        
class DistrictForm(forms.ModelForm):
    class Meta:
        model = District
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'data-limit-chars': '100'}),
        }
    def clean_name(self):
        val = self.cleaned_data.get('name')
        validate_char_limit(val, 100)
        return val
class InstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ['name', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'data-limit-chars': '150'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'data-limit-chars': '255'}),
        }
    def clean_name(self):
        val = self.cleaned_data.get('name')
        validate_char_limit(val, 150)
        return val

from accounts.models import CustomUser

class SchoolAdminForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False, help_text="Yangi foydalanuvchi uchun majburiy. Tahrirlashda bo'sh qoldirsa o'zgarmaydi.")
    
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'school', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'school': forms.Select(attrs={'class': 'form-control'}),
        }
    def clean_username(self):
        val = self.cleaned_data.get('username')
        validate_char_limit(val, 50)
        return val
    def clean_first_name(self):
        val = self.cleaned_data.get('first_name')
        validate_char_limit(val, 50)
        return val
    def clean_last_name(self):
        val = self.cleaned_data.get('last_name')
        validate_char_limit(val, 50)
        return val

class UnifiedSchoolForm(forms.ModelForm):
    admin_username = forms.CharField(
        max_length=150, 
        required=True, 
        label=_("Admin login (username)"),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    admin_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
        label=_("Admin paroli")
    )
    admin_password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
        label=_("Parolni tasdiqlash")
    )

    class Meta:
        model = School
        fields = ['district', 'name', 'address', 'contact']
        widgets = {
            'district': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    field_order = ['district', 'name', 'address', 'contact', 'admin_username', 'admin_password', 'admin_password_confirm']

    def clean_admin_username(self):
        username = self.cleaned_data.get('admin_username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError(_("Ushbu login band. Iltimos boshqasini tanlang."))
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("admin_password")
        confirm = cleaned_data.get("admin_password_confirm")

        if password and confirm and password != confirm:
            self.add_error('admin_password_confirm', _("Parollar mos kelmadi."))
        return cleaned_data
