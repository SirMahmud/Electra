from django.urls import path
from . import views

app_name = 'voters'

urlpatterns = [
    # Dashboards - CHANGED URLS to avoid /admin/ conflict
    path('voter/dashboard/', views.voter_dashboard, name='voter_dashboard'),
    path('staff/dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Changed from admin/dashboard/
    path('super-admin/dashboard/', views.super_admin_dashboard, name='super_admin_dashboard'),

    # User Management (Super Admin)
    path('super-admin/users/', views.manage_users, name='manage_users'),
    path('super-admin/users/<int:pk>/change-role/', views.change_user_role, name='change_user_role'),
]

