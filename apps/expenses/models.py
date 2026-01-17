"""
Expenses Models

This module handles operational expense tracking.

Business Logic:
- Expenses are separate from inventory costs (Cost of Goods Sold).
- Uses simple 'soft delete' to allow restoring accidental deletions.
- Expenses are categorized by 'item' (currently free text, potentially categorical in future).

Models:
- Expense: Represents a single financial outflow.
"""

from django.db import models
from django.utils import timezone
from apps.core.models import UserTrackingModel


class ExpenseManager(models.Manager):
    """
    Default manager that filters out soft-deleted expenses.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class ArchivedExpenseManager(models.Manager):
    """
    Manager to retrieve only soft-deleted expenses for restoration/audit.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=True)


class Expense(UserTrackingModel):
    """
    Represents an operational expense (e.g., Rent, Packaging, Transport).
    
    Attributes:
        item (CharField): Description of the expense.
        cost (DecimalField): Monetary value.
        expense_date (DateField): Date incurred.
        notes (TextField): Additional details.
        
        is_deleted (bool): Soft-delete flag.
        deleted_at (DateTimeField): When it was deleted.
        deleted_reason (TextField): Justification.
        deleted_by (User): Who deleted it.
    """
    item = models.CharField(max_length=200)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField()
    notes = models.TextField(blank=True)
    
    # Soft delete fields
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_reason = models.TextField(blank=True)
    deleted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='expenses_deleted',
        null=True,
        blank=True
    )
    
    # Managers
    objects = ExpenseManager()
    archived = ArchivedExpenseManager()
    all_objects = models.Manager()
    
    class Meta:
        ordering = ['-expense_date', '-created_at']
    
    def __str__(self):
        return f"{self.item} - ₦{self.cost}"
        
    def soft_delete(self, user, reason):
        """
        Mark expense as deleted.
        
        Args:
            user (User): Admin performing the action.
            reason (str): Why it is being deleted.
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.deleted_reason = reason
        self.save()

    def restore(self):
        """Restore a soft-deleted expense."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.deleted_reason = ""
        self.save()
