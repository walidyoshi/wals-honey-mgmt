"""
Customers Admin Configuration

Customizes the Django admin interface for the Customer model.

Admin Classes:
- CustomerAdmin: Management interface for Customer records.
"""

from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """
    Admin interface for Customer model.
    
    Features:
        - Shows creation metadata (created_by, created_at).
        - Allows filtering by deleted status.
        - Organizes fields into collapsible sections for cleaner UI.
    """
    list_display = ['name', 'created_at', 'created_by', 'is_deleted']
    list_filter = ['is_deleted', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'modified_at', 'created_by', 'modified_by', 'deleted_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('name',)
        }),
        ('Deletion Info', {
            'fields': ('is_deleted', 'deleted_at', 'deleted_reason'),
            'classes': ('collapse',)
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'created_by', 'modified_at', 'modified_by'),
            'classes': ('collapse',)
        }),
    )
