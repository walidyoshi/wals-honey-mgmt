"""
Batch and AuditLog models
"""

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from apps.core.models import UserTrackingModel


class Batch(UserTrackingModel):
    """Individual jerrycan tracking"""
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
        return self.batch_id
    
    @property
    def group_number(self):
        """Extract group number from batch_id (e.g., G02 from A24G02)"""
        return self.batch_id[-3:] if len(self.batch_id) >= 3 else ''
    
    @property
    def total_bottles(self):
        """Total bottles produced from this jerrycan"""
        return (self.bottles_25cl + self.bottles_75cl + 
                self.bottles_1L + self.bottles_4L)


class AuditLog(models.Model):
    """Generic audit trail for all model changes"""
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
        return f"{self.content_type} #{self.object_id} - {self.field_name}"
