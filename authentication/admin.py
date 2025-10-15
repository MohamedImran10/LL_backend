from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User  # Default Django User for admin
from .models import AppUser

# Keep the default Django User admin for admin users
# Django will automatically register User model, so we don't need to customize it

@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email', 'name')
    ordering = ('-created_at',)
    readonly_fields = ('password_hash', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('email', 'name')}),
        ('Status', {'fields': ('is_active',)}),
        ('Security', {'fields': ('password_hash',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
