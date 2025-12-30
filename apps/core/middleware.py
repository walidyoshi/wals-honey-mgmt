"""
Middleware for tracking current user in thread-local storage
"""

import threading

_user = threading.local()


class UserTrackingMiddleware:
    """Store current user in thread-local storage for auto-assignment"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        _user.value = getattr(request, 'user', None)
        response = self.get_response(request)
        return response


def get_current_user():
    """Get current user from thread-local storage"""
    return getattr(_user, 'value', None)
