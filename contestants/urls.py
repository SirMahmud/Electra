from django.urls import path
from . import views

app_name = 'contestants'

urlpatterns = [
    # Position URLs
    path(
        'election/<int:election_pk>/add-position/',
        views.add_position,
        name='add_position'
    ),
    path(
        'position/<int:pk>/edit/',
        views.edit_position,
        name='edit_position'
    ),
    path(
        'position/<int:pk>/delete/',
        views.delete_position,
        name='delete_position'
    ),
    
    # Contestant URLs
    path(
        'election/<int:election_pk>/add-contestant/',
        views.add_contestant,
        name='add_contestant'
    ),
    path(
        '<int:pk>/edit/',
        views.edit_contestant,
        name='edit_contestant'
    ),
    path(
        '<int:pk>/delete/',
        views.delete_contestant,
        name='delete_contestant'
    ),
]