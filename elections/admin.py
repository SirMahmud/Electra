from django.contrib import admin
from .models import Election


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'start_date', 'end_date', 'results_published', 'created_by']
    list_filter = ['status', 'results_published', 'created_at']
    search_fields = ['title', 'description']
    date_hierarchy = 'start_date'
    ordering = ['-created_at']