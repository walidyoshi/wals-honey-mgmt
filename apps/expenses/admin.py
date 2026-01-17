"""
Expenses Admin Configuration

Customizes Django Admin for Expense management.

Classes:
- ExpenseAdmin: Admin interface for expenses.
"""

from django.contrib import admin
from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """
    Admin configuration for Expense model.
    
    Features:
        - Shows deleted items (overrides get_queryset).
        - Filter by date and deletion status.
    """
    list_display = ['item', 'cost', 'expense_date', 'is_deleted', 'created_by']
    list_filter = ['expense_date', 'is_deleted', 'created_at']
    search_fields = ['item', 'notes']
    readonly_fields = ['created_at', 'modified_at', 'created_by', 'modified_by', 'deleted_at', 'deleted_by']
    
    def get_queryset(self, request):
        """Retrieve all objects including soft-deleted ones."""
        return self.model.all_objects.all()
