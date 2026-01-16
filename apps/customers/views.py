"""
Customer views
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.db.models import Q
from .models import Customer


class CustomerListView(LoginRequiredMixin, ListView):
    """List all customers with search"""
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Customer.objects.filter(is_deleted=False)
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset


class CustomerDetailView(LoginRequiredMixin, DetailView):
    """Show customer details and purchase history"""
    model = Customer
    template_name = 'customers/customer_detail.html'
    context_object_name = 'customer'
    
    def get_queryset(self):
        return Customer.objects.filter(is_deleted=False)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get sales for this customer
        context['sales'] = self.object.sales.filter(is_deleted=False).order_by('-sale_date')[:20]
        return context


class CustomerAutocompleteView(LoginRequiredMixin, ListView):
    """HTMX endpoint for customer autocomplete"""
    model = Customer
    template_name = 'customers/partials/autocomplete_results.html'
    context_object_name = 'customers'
    
    def get_queryset(self):
        # HTMX sends the input value with the field name 'customer_name'
        query = self.request.GET.get('customer_name', '')
        if query:
            return Customer.objects.filter(
                is_deleted=False,
                name__icontains=query
            )[:10]
        return Customer.objects.none()
