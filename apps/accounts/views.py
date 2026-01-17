"""
Accounts Views

This module handles user authentication views.

Views:
- CustomLoginView: Renders the login page and handles authentication.
"""

from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy


class CustomLoginView(LoginView):
    """
    Custom login view using the 'accounts/login.html' template.
    
    URL: /accounts/login/
    Template: accounts/login.html
    
    Behavior:
        - Displays login form.
        - Redirects authenticated users to the dashboard (redirect_authenticated_user=True).
    """
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
