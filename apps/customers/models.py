"""
Customer model
"""

from django.db import models
from apps.core.models import UserTrackingModel


class Customer(UserTrackingModel):
    """Customer/client information with soft delete support"""
    name = models.CharField(max_length=200, unique=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
