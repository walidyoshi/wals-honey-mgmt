"""
Core Models

This module provides abstract base models used throughout the application to ensure
consistency in data tracking and auditing.

Business Logic:
- All critical records must support standard auditing (creation/modification timestamps).
- Records involving business transactions must track *who* created or modified them
  for accountability.

Models:
- TimeStampedModel: Adds created_at and modified_at fields.
- UserTrackingModel: Adds created_by and modified_by fields with auto-assignment logic.
"""

from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base class that provides self-updating 'created_at' and 'modified_at' fields.
    
    Attributes:
        created_at (DateTimeField): Auto-set to current time when object is first created.
        modified_at (DateTimeField): Auto-updated to current time whenever object is saved.
    
    Usage:
        Inherit from this class to add timestamp tracking to any model.
        
    Example:
        class MyModel(TimeStampedModel):
            ...
    """
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class UserTrackingModel(TimeStampedModel):
    """
    Abstract base class that automatically tracks the user who created or modified a record.
    
    Logic:
        - Relies on 'core.middleware.UserTrackingMiddleware' to fetch the current user
          from the request context (via thread-local storage).
        - If a user is logged in, 'created_by' is set on creation and 'modified_by'
          on every save.
    
    Attributes:
        created_by (ForeignKey): Reference to the User who created the record.
        modified_by (ForeignKey): Reference to the User who last modified the record.
    
    Relationships:
        - users (ForeignKey to accounts.User)
    
    Methods:
        save(): Overridden to automatically populateto user fields.
    """
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
        """
        Save the model instance, automatically setting user tracking fields.
        
        Fetches the current user from middleware. If authenticated:
        - Sets 'created_by' only if the instance is new (no primary key).
        - Always updates 'modified_by'.
        
        Args:
            *args: Positional arguments passed to parent save().
            **kwargs: Keyword arguments passed to parent save().
        """
        from .middleware import get_current_user
        user = get_current_user()
        # Only assign if a real user is found (e.g. not during automated scripts without context)
        if user and user.is_authenticated:
            if not self.pk:
                self.created_by = user
            self.modified_by = user
        super().save(*args, **kwargs)
