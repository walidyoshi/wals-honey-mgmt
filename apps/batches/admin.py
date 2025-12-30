"""
Admin configuration for batches app
"""

from django.contrib import admin
from .models import Batch, AuditLog


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ['batch_id', 'supply_date', 'total_bottles', 'price', 'created_by']
    list_filter = ['supply_date', 'created_at']
    search_fields = ['batch_id', 'source', 'notes']
    readonly_fields = ['created_at', 'modified_at', 'created_by', 'modified_by']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['content_type', 'object_id', 'field_name', 'old_value', 'new_value', 'changed_at', 'changed_by']
    list_filter = ['content_type', 'changed_at', 'field_name']
    search_fields = ['old_value', 'new_value']
    readonly_fields = ['changed_at', 'changed_by']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
