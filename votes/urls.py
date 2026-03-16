from django.urls import path
from . import views

app_name = 'votes'

urlpatterns = [
    path('election/<int:election_pk>/vote/', views.vote_view, name='vote'),
]