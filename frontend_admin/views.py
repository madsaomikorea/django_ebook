from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from schools.models import School, Institution
from accounts.models import CustomUser
from books.models import Book, BookIssue

@login_required(login_url='login')
def dashboard(request):
    context = {
        'school_count': School.objects.count(),
        'user_count': CustomUser.objects.count(),
        'total_books': Book.objects.count(),
        'active_loans': BookIssue.objects.filter(is_returned=False).count(),
        'schools': School.objects.all().order_by('-id')[:5],
        'institutions_count': Institution.objects.count(),
    }
    return render(request, 'admin_panel/dashboard.html', context)

@login_required(login_url='login')
def schools_list(request):
    from django.db.models import Count, Q
    schools = School.objects.annotate(
        student_count=Count('customuser', filter=Q(customuser__role='student'))
    ).order_by('-id')
    return render(request, 'admin_panel/schools.html', {'schools': schools})

@login_required(login_url='login')
def muassasalar_list(request):
    institutions = Institution.objects.all().order_by('-id')
    return render(request, 'admin_panel/muassasalar.html', {'institutions': institutions})

@login_required(login_url='login')
def statistics(request):
    from django.db.models import Count, Q
    from django.utils import timezone
    import datetime
    from books.models import Category, Book, BookIssue
    
    # Category stats
    category_stats = Category.objects.annotate(count=Count('book')).values('name', 'count')
    
    # Usage dynamics (last 7 days)
    today = timezone.now().date()
    days = []
    issue_counts = []
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        days.append(day.strftime('%d.%m'))
        count = BookIssue.objects.filter(issued_at__date=day).count()
        issue_counts.append(count)
        
    # Top schools
    from django.db.models import Count as DBCount
    top_schools = School.objects.annotate(
        reader_count=DBCount('customuser', filter=Q(customuser__role='student'))
    ).order_by('-reader_count')[:5]

    context = {
        'category_labels': [item['name'] for item in category_stats],
        'category_data': [item['count'] for item in category_stats],
        'usage_labels': days,
        'usage_data': issue_counts,
        'top_schools': top_schools,
    }
    return render(request, 'admin_panel/statistics.html', context)

@login_required(login_url='login')
def system_logs(request):
    from stats.models import ActionLog
    logs = ActionLog.objects.all().order_by('-created_at')[:20]
    return render(request, 'admin_panel/logs.html', {'logs': logs})

@login_required(login_url='login')
def all_users_list(request):
    users = CustomUser.objects.all().select_related('school').order_by('-date_joined')
    return render(request, 'admin_panel/all_users.html', {'users': users})

@login_required(login_url='login')
def all_books_list(request):
    books = Book.objects.all().select_related('school', 'category').order_by('-id')
    return render(request, 'admin_panel/all_books.html', {'books': books})

@login_required(login_url='login')
def all_active_loans_list(request):
    active_loans = BookIssue.objects.filter(is_returned=False).select_related('book__school', 'user').order_by('-issued_at')
    return render(request, 'admin_panel/all_active_loans.html', {'active_loans': active_loans})

@login_required(login_url='login')
def school_detail(request, pk):
    school = get_object_or_404(School, pk=pk)
    context = {
        'school': school,
        'student_count': CustomUser.objects.filter(school=school, role='student').count(),
        'book_count': Book.objects.filter(school=school).count(),
        'issued_count': BookIssue.objects.filter(book__school=school, is_returned=False).count(),
        'school_admin': CustomUser.objects.filter(school=school, role='school_admin').first(),
        'students': CustomUser.objects.filter(school=school, role='student').order_by('-date_joined')[:20],
        'books': Book.objects.filter(school=school).order_by('-id')[:20],
    }
    return render(request, 'admin_panel/school_detail.html', context)

from .forms import SchoolForm, InstitutionForm

@login_required(login_url='login')
def muassasa_add(request):
    if request.method == 'POST':
        form = InstitutionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('frontend_admin:muassasalar_list')
    else:
        form = InstitutionForm()
    return render(request, 'admin_panel/muassasa_form.html', {'form': form, 'title': 'Yangi muassasa qo\'shish'})

@login_required(login_url='login')
def muassasa_edit(request, pk):
    inst = get_object_or_404(Institution, pk=pk)
    if request.method == 'POST':
        form = InstitutionForm(request.POST, instance=inst)
        if form.is_valid():
            form.save()
            return redirect('frontend_admin:muassasalar_list')
    else:
        form = InstitutionForm(instance=inst)
    return render(request, 'admin_panel/muassasa_form.html', {'form': form, 'title': 'Muassasa ma\'lumotlarini tahrirlash'})

@login_required(login_url='login')
def muassasa_delete(request, pk):
    inst = get_object_or_404(Institution, pk=pk)
    if request.method == 'POST':
        inst.delete()
        return redirect('frontend_admin:muassasalar_list')
    return render(request, 'admin_panel/confirm_delete.html', {'object': inst, 'type': 'muassasani'})

@login_required(login_url='login')
def school_add(request):
    if request.method == 'POST':
        form = SchoolForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('frontend_admin:schools_list')
    else:
        form = SchoolForm()
    return render(request, 'admin_panel/school_form.html', {'form': form, 'title': 'Yangi maktab qo\'shish'})

@login_required(login_url='login')
def school_edit(request, pk):
    school = get_object_or_404(School, pk=pk)
    if request.method == 'POST':
        form = SchoolForm(request.POST, instance=school)
        if form.is_valid():
            form.save()
            return redirect('frontend_admin:schools_list')
    else:
        form = SchoolForm(instance=school)
    return render(request, 'admin_panel/school_form.html', {'form': form, 'title': 'Maktab ma\'lumotlarini tahrirlash'})

@login_required(login_url='login')
def school_delete(request, pk):
    school = get_object_or_404(School, pk=pk)
    if request.method == 'POST':
        school.delete()
        return redirect('frontend_admin:schools_list')
    return render(request, 'admin_panel/confirm_delete.html', {'object': school, 'type': 'maktabni'})

from .forms import SchoolAdminForm

@login_required(login_url='login')
def admin_add(request):
    if request.method == 'POST':
        form = SchoolAdminForm(request.POST)
        if form.is_valid():
            admin = form.save(commit=False)
            admin.role = 'school_admin'
            if form.cleaned_data.get('password'):
                admin.set_password(form.cleaned_data['password'])
            admin.save()
            return redirect('frontend_admin:all_users_list')
    else:
        form = SchoolAdminForm()
    return render(request, 'admin_panel/muassasa_form.html', {'form': form, 'title': 'Yangi maktab admini qo\'shish'})

@login_required(login_url='login')
def admin_edit(request, pk):
    admin = get_object_or_404(CustomUser, pk=pk, role='school_admin')
    if request.method == 'POST':
        form = SchoolAdminForm(request.POST, instance=admin)
        if form.is_valid():
            if form.cleaned_data.get('password'):
                admin.set_password(form.cleaned_data['password'])
            form.save()
            return redirect('frontend_admin:all_users_list')
    else:
        form = SchoolAdminForm(instance=admin)
    return render(request, 'admin_panel/muassasa_form.html', {'form': form, 'title': 'Admin ma\'lumotlarini tahrirlash'})
