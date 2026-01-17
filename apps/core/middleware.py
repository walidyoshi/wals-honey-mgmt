"""
Core Middleware

Provides middleware components for global request handling and context management.

Classes:
    UserTrackingMiddleware: Captures the current user for model access.

Functions:
    get_current_user: Retrieves the thread-local user.
"""

import threading

# Thread-local storage to hold the value of the current request's user
_user = threading.local()


class UserTrackingMiddleware:
    """
    Middleware to globally track the currently logged-in user.
    
    How it works:
        1. Intercepts every incoming request.
        2. extracts 'request.user' and stores it in thread-local storage.
        3. This allows models (like UserTrackingModel) to access the current user
           in their 'save()' method without needing 'request' passed explicitly.
    
    Usage:
        Add 'apps.core.middleware.UserTrackingMiddleware' to MIDDLEWARE in settings.
    """
    
    def __init__(self, get_response):
        """
        Standard middleware initialization.
        
        Args:
            get_response: The next middleware or view in the chain.
        """
        self.get_response = get_response
    
    def __call__(self, request):
        """
        Process the request and store the user.
        
        Args:
            request (HttpRequest): The incoming Django request.
            
        Returns:
            HttpResponse: The response from the next link in the chain.
        """
        # Store user in thread-local storage
        _user.value = getattr(request, 'user', None)
        
        response = self.get_response(request)
        return response


def get_current_user():
    """
    Retrieve the current user from thread-local storage.
    
    Returns:
        User or None: The currently authenticated user, or None if not set.
    """
    return getattr(_user, 'value', None)
