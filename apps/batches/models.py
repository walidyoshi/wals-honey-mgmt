"""
Batches Models

This module handles the core inventory tracking: batches of honey (jerrycans).

Business Logic:
- A 'Batch' represents a single unit of acquisition (typically one jerrycan).
- Batch IDs are strictly formatted (e.g., A24G02) to encode:
    - Supplier/Region (First letter)
    - Year (Two digits, e.g., 24)
    - Group Number (Last 3 chars, e.g., G02) for grouping related batches.
- We track the conversion of bulk honey into packed bottles (25cl, 75cl, etc.).
- 'AuditLog' provides a generic way to track field-level changes for security.

Models:
- Batch: The inventory item.
- AuditLog: History of changes to any model (primarily Batches).
"""

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from apps.core.models import UserTrackingModel


class Batch(UserTrackingModel):
    """
    Represents a specific batch (jerrycan) of honey acquired from a supplier.
    
    Attributes:
        batch_id (CharField): Unique identifier (e.g., 'A24G02').
        price (DecimalField): Cost of the raw honey.
        tp_cost (DecimalField): Transport/logistic costs for this specific batch.
        supply_date (DateField): When the batch was acquired.
        source (CharField): Supplier name or origin region.
        bottles_25cl (int): Quantity of 25cl jars produced.
        bottles_75cl (int): Quantity of 75cl jars produced.
        bottles_1L (int): Quantity of 1L jars produced.
        bottles_4L (int): Quantity of 4L jars produced.
        notes (TextField): Optional remarks.
    
    Properties:
        group_number: Extracts the group identifier (e.g., 'G02') from the batch_id.
        total_bottles: Sum of all bottle sizes produced from this batch.
    
    Example:
        >>> batch = Batch.objects.create(batch_id="A24G02", price=500.00)
        >>> batch.group_number
        'G02'
    """
    batch_id = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Format: A24G02 (A24=jerrycan ID, G02=group number)"
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Purchase price for this jerrycan"
    )
    tp_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Transport Cost"
    )
    supply_date = models.DateField(null=True, blank=True)
    source = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Supplier name or location"
    )
    
    # Bottle production counts
    bottles_25cl = models.PositiveIntegerField(default=0)
    bottles_75cl = models.PositiveIntegerField(default=0)
    bottles_1L = models.PositiveIntegerField(default=0, verbose_name="Bottles 1L")
    bottles_4L = models.PositiveIntegerField(default=0, verbose_name="Bottles 4L")
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-supply_date', '-created_at']
        verbose_name_plural = "Batches"
    
    def __str__(self):
        """Return batch ID."""
        return self.batch_id
    
    @property
    def group_number(self):
        """
        Extract group number from batch_id (e.g., G02 from A24G02).
        
        Returns:
            str: The last 3 characters if valid, else empty string.
        """
        return self.batch_id[-3:] if len(self.batch_id) >= 3 else ''
    
    @property
    def total_bottles(self):
        """
        Calculate total bottles produced from this jerrycan across all sizes.
        
        Returns:
            int: Sum of all bottle fields.
        """
        return (self.bottles_25cl + self.bottles_75cl + 
                self.bottles_1L + self.bottles_4L)


class AuditLog(models.Model):
    """
    Generic audit trail for tracking field-level changes in models.
    
    Logic:
        - Uses GenericForeignKey to link to any model (loose coupling).
        - created via signals (see apps.batches.signals).
        - Read-only in Admin interface to preserve integrity.
        
    Attributes:
        content_type (ForeignKey): The model class being tracked.
        object_id (int): The primary key of the tracked object.
        field_name (CharField): The name of the field that was changed.
        old_value (TextField): Previous value.
        new_value (TextField): New updated value.
        changed_at (DateTimeField): When the change occurred.
        changed_by (ForeignKey): Who made the change.
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT
    )
    
    class Meta:
        ordering = ['-changed_at']
    
    def __str__(self):
        """Return summary of change."""
        return f"{self.content_type} #{self.object_id} - {self.field_name}"
