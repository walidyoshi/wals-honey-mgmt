"""
Expense model
"""

from django.db import models
from django.utils import timezone
from apps.core.models import UserTrackingModel


class ExpenseManager(models.Manager):
    """Custom manager to exclude deleted expenses by default"""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class ArchivedExpenseManager(models.Manager):
    """Manager to find deleted expenses"""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=True)


class Expense(UserTrackingModel):
    """Business expense tracking with soft delete support"""
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
        """Perform soft delete"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.deleted_reason = reason
        self.save()

    def restore(self):
        """Restore deleted expense"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.deleted_reason = ""
        self.save()
