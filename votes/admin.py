from django.contrib import admin
from .models import Vote


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'election', 'contestant', 'voted_at']
    list_filter = ['election', 'voted_at']
    search_fields = ['user__email', 'user__voter_id', 'contestant__name']
    date_hierarchy = 'voted_at'
    ordering = ['-voted_at']
    
    def has_add_permission(self, request):
        # Prevent adding votes through admin
        return False
    
    def has_change_permission(self, request, obj=None):
        # Prevent changing votes through admin
        return False