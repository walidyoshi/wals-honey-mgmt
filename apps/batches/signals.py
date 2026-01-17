"""
Batches Signals

This module handles automatic side-effects for Batch operations, specifically audit logging.

Signals:
- track_batch_changes: Listens for pre_save events to record field modifications.
"""

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Batch, AuditLog


@receiver(pre_save, sender=Batch)
def track_batch_changes(sender, instance, **kwargs):
    """
    Compare old and new values of a Batch before saving and create AuditLog entries.
    
    Triggered:
        Before a Batch instance is saved (pre_save).
    
    Args:
        sender: The Batch class.
        instance: The specific batch being saved.
        **kwargs: Signal arguments.
    
    Logic:
        1. Checks if instance has a PK (update vs create).
        2. If update, fetches the *original* version from DB.
        3. Iterates through sensitive fields (bottles, price, etc.).
        4. If a difference is found, creates an AuditLog record.
        
    Attribution:
        Records who made the change via 'instance.modified_by', which is populated
        by UserTrackingMiddleware/UserTrackingModel before this signal fires.
    """
    if instance.pk:  # Only for updates
        try:
            old_instance = Batch.objects.get(pk=instance.pk)
            fields_to_track = [
                'bottles_25cl', 'bottles_75cl', 'bottles_1L', 'bottles_4L',
                'price', 'tp_cost', 'supply_date', 'source'
            ]
            
            for field in fields_to_track:
                old_value = str(getattr(old_instance, field))
                new_value = str(getattr(instance, field))
                
                if old_value != new_value:
                    # We need a user to attribute the change to
                    # Since signals don't have access to request, we rely on the modified_by field
                    # which should have been set by the view/form processing the request
                    # OR by the UserTrackingMiddleware if available
                    
                    AuditLog.objects.create(
                        content_type=ContentType.objects.get_for_model(Batch),
                        object_id=instance.pk,
                        field_name=field,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=instance.modified_by
                    )
        except Batch.DoesNotExist:
            pass
