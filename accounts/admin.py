from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, VoterIDRegistry


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'voter_id', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active', 'date_joined']
    search_fields = ['email', 'voter_id', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('voter_id', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('role', 'is_active')}),
        ('Important Dates', {'fields': ('date_joined',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'voter_id', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(VoterIDRegistry)
class VoterIDRegistryAdmin(admin.ModelAdmin):
    list_display = ['voter_id', 'status', 'registered_by', 'registered_at', 'created_at']
    list_filter = ['status', 'registered_at', 'created_at']
    search_fields = ['voter_id', 'notes']
    ordering = ['-created_at']
    readonly_fields = ['registered_by', 'registered_at', 'created_at', 'updated_at']