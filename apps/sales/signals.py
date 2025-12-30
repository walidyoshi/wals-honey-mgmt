"""
Signals for sales and payment tracking
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Payment, Sale
from apps.batches.models import AuditLog


@receiver(post_save, sender=Payment)
@receiver(post_delete, sender=Payment)
def update_sale_payment_status(sender, instance, **kwargs):
    """Auto-update sale payment status when payment added/deleted"""
    instance.sale.update_payment_status()


@receiver(pre_save, sender=Sale)
def track_sale_changes(sender, instance, **kwargs):
    """Track changes to sale fields"""
    if instance.pk:
        try:
            old_instance = Sale.objects.get(pk=instance.pk)
            fields_to_track = [
                'customer_name', 'bottle_type', 'unit_price', 
                'quantity', 'payment_status', 'is_wholesale'
            ]
            
            for field in fields_to_track:
                old_value = str(getattr(old_instance, field))
                new_value = str(getattr(instance, field))
                
                if old_value != new_value:
                    AuditLog.objects.create(
                        content_type=ContentType.objects.get_for_model(Sale),
                        object_id=instance.pk,
                        field_name=field,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=instance.modified_by
                    )
        except Sale.DoesNotExist:
            pass
