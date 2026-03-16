from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # User Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Voter ID Management (Super Admin Only)
    path('voter-ids/', views.manage_voter_ids, name='manage_voter_ids'),
    path('voter-ids/add/', views.add_voter_id, name='add_voter_id'),
    path('voter-ids/bulk-upload/', views.bulk_upload_voter_ids, name='bulk_upload_voter_ids'),
    path('voter-ids/<int:pk>/edit/', views.edit_voter_id, name='edit_voter_id'),
    path('voter-ids/<int:pk>/delete/', views.delete_voter_id, name='delete_voter_id'),
]