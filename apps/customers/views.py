"""
Customers Views

This module provides interfaces for viewing and managing customers.

Views:
- CustomerListView: Browsing all active customers.
- CustomerDetailView: Viewing specific customer profile and history.
- CustomerAutocompleteView: HTMX endpoint for dynamic customer search in forms.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Customer


class CustomerListView(LoginRequiredMixin, ListView):
    """
    Display a paginated list of active customers.
    
    URL: /customers/
    Template: customers/customer_list.html
    
    Features:
        - Filters out soft-deleted customers.
        - Supports name search via 'search' GET parameter.
    
    Context Variables:
        customers (QuerySet): List of Customer objects.
    """
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 50
    
    def get_queryset(self):
        """
        Return filtered customer list.
        
        Logic:
            1. Exclude deleted customers.
            2. If 'search' param exists, filter by name (case-insensitive).
            
        Returns:
            QuerySet: Filtered list of Customers.
        """
        queryset = Customer.objects.filter(is_deleted=False)
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset


class CustomerDetailView(LoginRequiredMixin, DetailView):
    """
    Display details for a specific customer.
    
    URL: /customers/<pk>/
    Template: customers/customer_detail.html
    
    Context Variables:
        customer (Customer): The customer instance.
        sales (QuerySet): Top 20 recent sales for this customer.
    """
    model = Customer
    template_name = 'customers/customer_detail.html'
    context_object_name = 'customer'
    
    def get_queryset(self):
        """Ensure we don't show deleted customers details (optional safety)."""
        return Customer.objects.filter(is_deleted=False)
    
    def get_context_data(self, **kwargs):
        """
        Add sales history to context.
        
        Returns:
            dict: Context with 'sales' key added.
        """
        context = super().get_context_data(**kwargs)
        # Get sales for this customer
        # Note: 'sales' is the related_name from the Sale model
        context['sales'] = self.object.sales.filter(is_deleted=False).order_by('-sale_date')[:20]
        return context


class CustomerAutocompleteView(LoginRequiredMixin, ListView):
    """
    HTMX-powered view for searching customers in forms (e.g., Sale form).
    
    URL: /customers/autocomplete/
    Template: customers/partials/autocomplete_results.html
    
    Usage:
        Called via hx-get when typing in the customer input field.
        
    Query Parameters:
        customer_name (str): The search term.
        
    Returns:
        HTML fragment: List of matching customer <li> elements.
    """
    model = Customer
    template_name = 'customers/partials/autocomplete_results.html'
    context_object_name = 'customers'
    
    def get_queryset(self):
        """
        Return top 10 matching customers.
        
        Returns:
            QuerySet: Customers matching the search term, or empty if no term.
        """
        # HTMX sends the input value with the field name 'customer_name'
        query = self.request.GET.get('customer_name', '')
        if query:
            return Customer.objects.filter(
                is_deleted=False,
                name__icontains=query
            )[:10]
        return Customer.objects.none()
