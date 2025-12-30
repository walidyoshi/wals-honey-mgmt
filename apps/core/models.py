"""
Base model classes for the application
"""

from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base class for timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class UserTrackingModel(TimeStampedModel):
    """Abstract base class for user tracking"""
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='%(class)s_created',
        editable=False
    )
    modified_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='%(class)s_modified',
        editable=False
    )
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        from .middleware import get_current_user
        user = get_current_user()
        if user and user.is_authenticated:
            if not self.pk:
                self.created_by = user
            self.modified_by = user
        super().save(*args, **kwargs)
