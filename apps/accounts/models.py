"""
Accounts Models

This module handles user management and authentication.

Business Logic:
- The system uses Email as the primary identifier for authentication (not username).
- 'full_name' is required for display purposes.

Models:
- User: Custom user model extending AbstractUser (removing username field).
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of usernames.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        
        Args:
            email (str): The email address (required).
            password (str, optional): The user's password.
            **extra_fields: Additional fields for the user model.
            
        Returns:
            User: The created user instance.
            
        Raises:
            ValueError: If email is not set.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a Superuser with the given email and password.
        
        Args:
            email (str): The email address.
            password (str): The superuser's password.
            **extra_fields: Additional fields.
            
        Returns:
            User: The created superuser.
            
        Raises:
            ValueError: If is_staff or is_superuser is not True.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model that relies on email for authentication.
    
    Attributes:
        username (None): Disabled.
        email (EmailField): Primary unique identifier.
        full_name (CharField): User's full display name.
    
    Relationships:
        groups (ManyToManyField): Django auth groups.
        user_permissions (ManyToManyField): Specific permissions.
    """
    username = None
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    objects = CustomUserManager()
    
    def __str__(self):
        """Return the user's email."""
        return self.email
