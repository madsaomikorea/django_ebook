from django.urls import path
from . import views

app_name = 'frontend_user'

urlpatterns = [
    path('', views.library, name='library'),
    path('my-books/', views.my_books, name='my_books'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('book/<int:pk>/reserve/', views.reserve_book, name='reserve_book'),
    path('request/<int:pk>/qr/', views.request_qr, name='request_qr'),
    path('issue/<int:pk>/qr/', views.issue_qr, name='issue_qr'),
    path('request/<int:pk>/status/', views.check_request_status, name='check_request_status'),
    path('token/<str:type>/<int:pk>/', views.get_rotating_token, name='get_rotating_token'),
]
