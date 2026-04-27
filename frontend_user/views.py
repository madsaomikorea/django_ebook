from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from books.models import Book, Category
from django.db.models import Q
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages

@login_required(login_url='login')
def library(request):
    query = request.GET.get('q')
    books = Book.objects.filter(school=request.user.school).order_by('-borrow_count')
    
    if query:
        books = books.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    # Get all categories for quick filters
    categories = Category.objects.all()
        
    return render(request, 'user_panel/library.html', {
        'books': books,
        'categories': categories,
        'current_query': query or ''
    })

@login_required(login_url='login')
def my_books(request):
    from books.models import BookIssue, BookRequest
    issues = BookIssue.objects.filter(user=request.user, is_returned=False).order_by('-issued_at')
    requests = BookRequest.objects.filter(user=request.user, status='pending').order_by('-requested_at')
    history = BookIssue.objects.filter(user=request.user, is_returned=True).order_by('-returned_at')
    
    return render(request, 'user_panel/my_books.html', {
        'issues': issues,
        'requests': requests,
        'history': history
    })

@login_required(login_url='login')
def profile(request):
    if request.user.role == 'school_admin':
        return redirect('frontend_school:profile')
    if request.user.role == 'superuser' or request.user.is_superuser:
        return redirect('frontend_admin:profile')
    return render(request, 'user_panel/profile.html')

@login_required(login_url='login')
def profile_edit(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()
        return redirect('frontend_user:profile')
    return render(request, 'user_panel/profile_edit.html')

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Parolingiz muvaffaqiyatli o\'zgartirildi!')
            return redirect('frontend_user:profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'user_panel/password_change.html', {'form': form})

@login_required(login_url='login')
def book_detail(request, pk):
    book = Book.objects.get(pk=pk)
    return render(request, 'user_panel/book_detail.html', {'book': book})

@login_required(login_url='login')
def reserve_book(request, pk):
    from books.models import BookRequest
    from django.shortcuts import redirect
    import uuid
    
    book = Book.objects.get(pk=pk)
    
    # Check if already requested
    request_obj = BookRequest.objects.filter(user=request.user, book=book, status='pending').first()
    if not request_obj:
        request_obj = BookRequest.objects.create(user=request.user, book=book)
        
    if not request_obj.qr_token:
        # Generate unique token for QR if it doesn't exist
        token = f"REQ_{request_obj.id}_{uuid.uuid4().hex[:8]}"
        request_obj.qr_token = token
        request_obj.save()
        
    return redirect('frontend_user:request_qr', pk=request_obj.pk)

@login_required(login_url='login')
def request_qr(request, pk):
    from books.models import BookRequest
    import uuid
    request_obj = BookRequest.objects.get(pk=pk, user=request.user)
    
    if not request_obj.qr_token:
        token = f"REQ_{request_obj.id}_{uuid.uuid4().hex[:8]}"
        request_obj.qr_token = token
        request_obj.save()
        
    return render(request, 'user_panel/request_qr.html', {'request_obj': request_obj})

@login_required(login_url='login')
def issue_qr(request, pk):
    from books.models import BookIssue
    import uuid
    issue_obj = BookIssue.objects.get(pk=pk, user=request.user)
    
    if not issue_obj.qr_token:
        issue_obj.qr_token = f"RET_{issue_obj.id}_{uuid.uuid4().hex[:8]}"
        issue_obj.save()
        
    return render(request, 'user_panel/issue_qr.html', {'issue_obj': issue_obj})

from django.http import JsonResponse
def check_request_status(request, pk):
    from books.models import BookRequest
    request_obj = get_object_or_404(BookRequest, pk=pk)
    return JsonResponse({'status': request_obj.status})

@login_required(login_url='login')
def check_return_status(request, pk):
    from books.models import BookIssue
    issue_obj = get_object_or_404(BookIssue, pk=pk)
    return JsonResponse({'is_returned': issue_obj.is_returned})

@login_required(login_url='login')
def get_rotating_token(request, type, pk):
    from accounts.utils import generate_dynamic_token
    if type == 'request':
        return JsonResponse({'token': generate_dynamic_token('REQ', pk)})
    elif type == 'issue':
        return JsonResponse({'token': generate_dynamic_token('RET', pk)})
    return JsonResponse({'error': 'Invalid type'}, status=400)
