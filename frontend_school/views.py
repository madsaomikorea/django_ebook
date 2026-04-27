from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from accounts.models import CustomUser
from books.models import Book, BookIssue

from django.db.models import Sum
from django.utils.crypto import get_random_string
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import secrets
import string

@login_required(login_url='login')
def dashboard(request):
    school = request.user.school
    context = {}
    if school:
        recent_activities = BookIssue.objects.filter(book__school=school).order_by('-issued_at')[:5]
        stats = Book.objects.filter(school=school).aggregate(
            total_copies=Sum('total_count'),
            available_copies=Sum('available_count')
        )
        context = {
            'student_count': CustomUser.objects.filter(school=school, role='student').count(),
            'book_count': Book.objects.filter(school=school).count(),
            'total_copies': stats['total_copies'] or 0,
            'available_copies': stats['available_copies'] or 0,
            'issued_count': BookIssue.objects.filter(book__school=school, is_returned=False).count(),
            'recent_activities': recent_activities,
        }
    return render(request, 'school_panel/dashboard.html', context)

@login_required(login_url='login')
def students_list(request):
    school = request.user.school
    query = request.GET.get('q')
    students = CustomUser.objects.filter(school=school, role='student')
    
    if query:
        from django.db.models import Q
        students = students.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(grade__icontains=query)
        )
        
    students = students.order_by('last_name', 'first_name')
    return render(request, 'school_panel/students.html', {'students': students, 'query': query})

@login_required(login_url='login')
def teachers_list(request):
    school = request.user.school
    query = request.GET.get('q')
    teachers = CustomUser.objects.filter(school=school, role='teacher')
    
    if query:
        from django.db.models import Q
        teachers = teachers.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
        
    teachers = teachers.order_by('last_name', 'first_name')
    return render(request, 'school_panel/teachers.html', {'teachers': teachers, 'query': query})

@login_required(login_url='login')
def books_list(request):
    school = request.user.school
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    no_cover = request.GET.get('no_cover')
    
    books = Book.objects.filter(school=school)
    
    if query:
        books = books.filter(title__icontains=query)
    
    if category_id:
        books = books.filter(category_id=category_id)
        
    if no_cover == '1':
        from django.db.models import Q
        books = books.filter(Q(cover='') | Q(cover__isnull=True))
        
    books = books.order_by('title')
    
    from books.models import Category
    categories = Category.objects.all().order_by('name')
    
    return render(request, 'school_panel/books.html', {
        'books': books, 
        'categories': categories,
        'query': query,
        'selected_category': int(category_id) if category_id else None,
        'no_cover': no_cover == '1'
    })

@login_required(login_url='login')
def issued_books_list(request):
    school = request.user.school
    issues = BookIssue.objects.filter(book__school=school, is_returned=False).order_by('-issued_at')
    return render(request, 'school_panel/issued_books.html', {'issues': issues})

@login_required(login_url='login')
def news_list(request):
    from .models import News
    school = request.user.school
    news = News.objects.filter(school=school).order_by('-created_at')
    return render(request, 'school_panel/news.html', {'news': news})

@login_required(login_url='login')
def qr_unified(request):
    return render(request, 'school_panel/qr_unified.html')

@csrf_exempt
def process_qr_unified(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token', '')
            
            if token.startswith('REQ_'):
                return process_qr(request)
            elif token.startswith('RET_'):
                return process_receive_qr(request)
            else:
                return JsonResponse({'status': 'error', 'message': 'Noma\'lum QR-kod turi. Iltimos, kitob berish yoki qaytarish kodini skanerlang.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'})



@csrf_exempt
def process_qr(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')
            
            from accounts.utils import verify_dynamic_token
            request_id = verify_dynamic_token(token, 'REQ')
            
            if not request_id:
                return JsonResponse({'status': 'error', 'message': 'Eski yoki noto\'g\'ri QR-kod. Iltimos, o\'quvchi telefonida kodni yangilasini kutib turing.'})
            
            from books.models import BookRequest, BookIssue
            from stats.models import ActionLog
            
            try:
                request_obj = BookRequest.objects.get(id=request_id, status='pending')
            except BookRequest.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Bron topilmadi yoki allaqachon tasdiqlangan'})
            
            # Check if book is available
            book = request_obj.book
            if book.available_count <= 0:
                return JsonResponse({'status': 'error', 'message': 'Kitob qolmagan'})
            
            # Process: update request and create issue
            request_obj.status = 'approved'
            request_obj.save()
            
            issue = BookIssue.objects.create(book=book, user=request_obj.user)
            
            book.available_count -= 1
            book.borrow_count += 1
            book.save()

            # Log action
            ActionLog.objects.create(
                user=request.user,
                action_type='ISSUE',
                message=f"{request_obj.user.username}ga '{book.title}' kitobi berildi"
            )
            
            return JsonResponse({
                'status': 'success', 
                'message': f'Kitob muvaffaqiyatli berildi: {book.title}',
                'student': f'{request_obj.user.first_name} {request_obj.user.last_name}'
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'})

@csrf_exempt
def process_receive_qr(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')
            
            from accounts.utils import verify_dynamic_token
            issue_id = verify_dynamic_token(token, 'RET')
            
            if not issue_id:
                return JsonResponse({'status': 'error', 'message': 'Eski yoki noto\'g\'ri QR-kod'})
                
            from books.models import BookIssue
            from django.utils import timezone
            from stats.models import ActionLog
            
            try:
                issue = BookIssue.objects.get(id=issue_id, is_returned=False)
            except BookIssue.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Ushbu kitob uchun faol topshirish topilmadi'})
            
            book = issue.book
            user = issue.user
            
            issue.is_returned = True
            issue.returned_at = timezone.now()
            issue.save()
            
            book.available_count += 1
            book.save()
            
            # Find and complete the associated request if it exists
            from books.models import BookRequest
            request_obj = BookRequest.objects.filter(book=book, user=user, status='approved').first()
            if request_obj:
                request_obj.status = 'completed'
                request_obj.save()

            # Log action
            ActionLog.objects.create(
                user=request.user,
                action_type='RETURN',
                message=f"{user.username}dan '{book.title}' kitobi qabul qilindi"
            )
            
            return JsonResponse({
                'status': 'success', 
                'message': f'Kitob muvaffaqiyatli qabul qilindi: {book.title}',
                'student': f'{user.first_name} {user.last_name}'
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'})

from .forms import BookForm, StudentForm, TeacherForm, NewsForm

@login_required(login_url='login')
def book_add(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.school = request.user.school
            book.save()
            return redirect('frontend_school:books_list')
    else:
        form = BookForm()
    return render(request, 'school_panel/book_form.html', {'form': form, 'title': 'Yangi kitob qo\'shish'})

@login_required(login_url='login')
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk, school=request.user.school)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return redirect('frontend_school:books_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'school_panel/book_form.html', {'form': form, 'title': 'Kitobni tahrirlash'})

@login_required(login_url='login')
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk, school=request.user.school)
    if request.method == 'POST':
        book.delete()
        return redirect('frontend_school:books_list')
    return render(request, 'school_panel/confirm_delete.html', {'object': book, 'type': 'kitobni'})

@login_required(login_url='login')
def student_add(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.school = request.user.school
            student.role = 'student'
            
            # Generate username if not provided
            if not student.username:
                # Format: s[school_id]_[grade]_[random4]
                school_id = student.school.id if student.school else 0
                grade_slug = student.grade.lower().replace(' ', '')
                random_suffix = get_random_string(4, allowed_chars=string.ascii_lowercase + string.digits)
                student.username = f"s{school_id}_{grade_slug}_{random_suffix}"
            
            # Generate random password if not provided
            password = form.cleaned_data.get('password')
            if not password:
                password = get_random_string(12)
                messages.success(request, f"Yangi o'quvchi uchun parol: {password}")
            
            student.set_password(password)
            student.save()
            return redirect('frontend_school:students_list')
    else:
        form = StudentForm()
    return render(request, 'school_panel/student_form.html', {'form': form, 'title': 'Yangi o\'quvchi qo\'shish'})

@login_required(login_url='login')
def student_edit(request, pk):
    student = get_object_or_404(CustomUser, pk=pk, school=request.user.school, role='student')
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            if form.cleaned_data.get('password'):
                student.set_password(form.cleaned_data['password'])
            form.save()
            return redirect('frontend_school:students_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'school_panel/student_form.html', {'form': form, 'title': 'O\'quvchi ma\'lumotlarini tahrirlash'})

@login_required(login_url='login')
def student_delete(request, pk):
    student = get_object_or_404(CustomUser, pk=pk, school=request.user.school, role='student')
    if request.method == 'POST':
        student.delete()
        return redirect('frontend_school:students_list')
    return render(request, 'school_panel/confirm_delete.html', {'object': student, 'type': 'o\'quvchini'})

@login_required(login_url='login')
def teacher_add(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            teacher = form.save(commit=False)
            teacher.school = request.user.school
            teacher.role = 'teacher'
            
            # Generate username if not provided
            if not teacher.username:
                # Format: t[school_id]_[random4]
                school_id = teacher.school.id if teacher.school else 0
                random_suffix = get_random_string(4, allowed_chars=string.ascii_lowercase + string.digits)
                teacher.username = f"t{school_id}_{random_suffix}"
            
            # Generate random password if not provided
            password = form.cleaned_data.get('password')
            if not password:
                password = get_random_string(12)
                messages.success(request, f"Yangi o'qituvchi uchun parol: {password}")
            
            teacher.set_password(password)
            teacher.save()
            return redirect('frontend_school:teachers_list')
    else:
        form = TeacherForm()
    return render(request, 'school_panel/teacher_form.html', {'form': form, 'title': 'Yangi o\'qituvchi qo\'shish'})

@login_required(login_url='login')
def teacher_edit(request, pk):
    teacher = get_object_or_404(CustomUser, pk=pk, school=request.user.school, role='teacher')
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            if form.cleaned_data.get('password'):
                teacher.set_password(form.cleaned_data['password'])
            form.save()
            return redirect('frontend_school:teachers_list')
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'school_panel/teacher_form.html', {'form': form, 'title': 'O\'qituvchi ma\'lumotlarini tahrirlash'})

@login_required(login_url='login')
def teacher_delete(request, pk):
    teacher = get_object_or_404(CustomUser, pk=pk, school=request.user.school, role='teacher')
    if request.method == 'POST':
        teacher.delete()
        return redirect('frontend_school:teachers_list')
    return render(request, 'school_panel/confirm_delete.html', {'object': teacher, 'type': 'o\'qituvchini'})

@login_required(login_url='login')
def news_add(request):
    from .models import News
    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            news.school = request.user.school
            news.save()
            return redirect('frontend_school:news_list')
    else:
        form = NewsForm()
    return render(request, 'school_panel/news_form.html', {'form': form, 'title': 'Yangi yangilik qo\'shish'})

@login_required(login_url='login')
def news_edit(request, pk):
    from .models import News
    news = get_object_or_404(News, pk=pk, school=request.user.school)
    if request.method == 'POST':
        form = NewsForm(request.POST, instance=news)
        if form.is_valid():
            form.save()
            return redirect('frontend_school:news_list')
    else:
        form = NewsForm(instance=news)
    return render(request, 'school_panel/news_form.html', {'form': form, 'title': 'Yangilikni tahrirlash'})

@login_required(login_url='login')
def news_delete(request, pk):
    from .models import News
    news = get_object_or_404(News, pk=pk, school=request.user.school)
    if request.method == 'POST':
        news.delete()
        return redirect('frontend_school:news_list')
    return render(request, 'school_panel/confirm_delete.html', {'object': news, 'type': 'yangilikni'})

@login_required(login_url='login')
def profile(request):
    return render(request, 'school_panel/profile.html')

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Parolingiz muvaffaqiyatli o\'zgartirildi!')
            return redirect('frontend_school:profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'school_panel/password_change.html', {'form': form})
