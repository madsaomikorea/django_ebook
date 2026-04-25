from django.urls import path
from . import views

app_name = 'frontend_admin'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('schools/', views.schools_list, name='schools_list'),
    path('schools/add/', views.school_add, name='school_add'),
    path('schools/<int:pk>/edit/', views.school_edit, name='school_edit'),
    path('schools/<int:pk>/delete/', views.school_delete, name='school_delete'),
    path('schools/<int:pk>/', views.school_detail, name='school_detail'),
    path('muassasalar/', views.muassasalar_list, name='muassasalar_list'),
    path('muassasalar/add/', views.muassasa_add, name='muassasa_add'),
    path('muassasalar/<int:pk>/edit/', views.muassasa_edit, name='muassasa_edit'),
    path('muassasalar/<int:pk>/delete/', views.muassasa_delete, name='muassasa_delete'),
    path('statistics/', views.statistics, name='statistics'),
    path('logs/', views.system_logs, name='system_logs'),
    path('users/', views.all_users_list, name='all_users_list'),
    path('books/', views.all_books_list, name='all_books_list'),
    path('active-loans/', views.all_active_loans_list, name='all_active_loans_list'),
    path('admin/add/', views.admin_add, name='admin_add'),
    path('admin/<int:pk>/edit/', views.admin_edit, name='admin_edit'),
]
