"""
Expenses Signals

This module manages automated audit tracking for Expenses.

Signals:
- track_expense_changes: Records field-level changes to expense records for audit purposes.
"""

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Expense
from apps.batches.models import AuditLog


@receiver(pre_save, sender=Expense)
def track_expense_changes(sender, instance, **kwargs):
    """
    Record changes to Expense fields in the Audit Log.
    
    Fields Tracked:
        - item, cost, expense_date, notes
        
    Triggered:
        Before Expense is saved (only for existing records).
    """
    if instance.pk:
        try:
            old_instance = Expense.all_objects.get(pk=instance.pk)
            fields_to_track = ['item', 'cost', 'expense_date', 'notes']
            
            for field in fields_to_track:
                old_value = str(getattr(old_instance, field))
                new_value = str(getattr(instance, field))
                
                if old_value != new_value:
                    AuditLog.objects.create(
                        content_type=ContentType.objects.get_for_model(Expense),
                        object_id=instance.pk,
                        field_name=field,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=instance.modified_by
                    )
        except Expense.DoesNotExist:
            pass
