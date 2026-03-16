from django.contrib import admin
from .models import Contestant, Position


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['title', 'election', 'order', 'get_vote_count']
    list_filter = ['election']
    search_fields = ['title', 'election__title']
    ordering = ['election', 'order', 'title']


@admin.register(Contestant)
class ContestantAdmin(admin.ModelAdmin):
    list_display = ['name', 'election', 'position', 'party', 'order', 'get_vote_count']
    list_filter = ['election', 'position']
    search_fields = ['name', 'party']
    ordering = ['election', 'position', 'order', 'name']