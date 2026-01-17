"""
Customers Models

This module handles detailed Customer Information.

Business Logic:
- Customers are rarely permanently deleted; instead, they are soft-deleted ('is_deleted')
  to preserve sales history.
- Names must be unique to avoid ambiguity.

Models:
- Customer: Represents the buyer of honey products.
"""

from django.db import models
from apps.core.models import UserTrackingModel


class Customer(UserTrackingModel):
    """
    Represents a Customer who purchases honey or related products.
    
    Inherits from UserTrackingModel to automatically track who created/modified this customer.
    
    Attributes:
        name (CharField): Unique name of the customer.
        is_deleted (BooleanField): Soft-delete flag.
        deleted_at (DateTimeField): When the customer was soft-deleted.
        deleted_reason (TextField): Reason for deletion.
        created_at (DateTimeField): Inherited from TimeStampedModel.
        modified_at (DateTimeField): Inherited from TimeStampedModel.
        created_by (ForeignKey): Inherited from UserTrackingModel.
        modified_by (ForeignKey): Inherited from UserTrackingModel.
    
    Relationships:
        - sales (Reverse ForeignKey from Sale model)
    
    Example:
        >>> customer = Customer.objects.create(name="Sweet Shop")
    """
    name = models.CharField(max_length=200, unique=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        """Return customer name."""
        return self.name
