"""
Customers URL Configuration
"""

from django.urls import path
from .views import CustomerListView, CustomerDetailView, CustomerAutocompleteView

app_name = 'customers'

urlpatterns = [
    path('', CustomerListView.as_view(), name='list'),
    path('<int:pk>/', CustomerDetailView.as_view(), name='detail'),
    path('autocomplete/', CustomerAutocompleteView.as_view(), name='autocomplete'),
]
