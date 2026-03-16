from django.urls import path
from . import views

app_name = 'elections'

urlpatterns = [
    # Election Management (Super Admin)
    path('create/', views.create_election, name='create_election'),
    path('<int:pk>/', views.manage_election, name='manage_election'),
    path('<int:pk>/edit/', views.edit_election, name='edit_election'),
    path('<int:pk>/delete/', views.delete_election, name='delete_election'),
    path('<int:pk>/start/', views.start_election, name='start_election'),
    path('<int:pk>/end/', views.end_election, name='end_election'),
    path('<int:pk>/publish/', views.publish_results, name='publish_results'),
    path('<int:pk>/toggle-visibility/', views.toggle_visibility, name='toggle_visibility'),
    
    # Results
    path('<int:pk>/results/', views.election_results, name='election_results'),
    
    # API endpoint for live charts
    path('<int:pk>/live-results/', views.get_live_results, name='get_live_results'),
]