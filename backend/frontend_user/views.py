from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from books.models import Book
from django.db.models import Q

@login_required(login_url='login')
def library(request):
    query = request.GET.get('q')
    books = Book.objects.all().order_by('-borrow_count')
    
    if query:
        books = books.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    # Filter by user's school if applicable
    if request.user.school:
        books = books.filter(school=request.user.school)
        
    return render(request, 'user_panel/library.html', {'books': books})

@login_required(login_url='login')
def my_books(request):
    from books.models import BookIssue, BookRequest
    issues = BookIssue.objects.filter(user=request.user, is_returned=False).order_by('-issued_at')
    requests = BookRequest.objects.filter(user=request.user).order_by('-requested_at')
    return render(request, 'user_panel/my_books.html', {
        'issues': issues,
        'requests': requests
    })

@login_required(login_url='login')
def profile(request):
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
    request_obj = BookRequest.objects.get(pk=pk)
    return JsonResponse({'status': request_obj.status})

@login_required(login_url='login')
def get_rotating_token(request, type, pk):
    from accounts.utils import generate_dynamic_token
    if type == 'request':
        return JsonResponse({'token': generate_dynamic_token('REQ', pk)})
    elif type == 'issue':
        return JsonResponse({'token': generate_dynamic_token('RET', pk)})
    return JsonResponse({'error': 'Invalid type'}, status=400)
