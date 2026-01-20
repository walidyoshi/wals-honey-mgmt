"""
Sales Views

This module manages the Sales workflow, including list, create, update, and special archival views.

Views:
- SaleListView: browsable sales history.
- SaleCreateView: POST entry for new sales.
- SaleArchiveView: Handles soft-deletion with reason capture.
- PaymentCreateView: HTMX-powered modal for adding payments.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView, View
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse

from .models import Sale, Payment
from .forms import SaleForm, PaymentForm, ArchiveSaleForm


class SaleListView(LoginRequiredMixin, ListView):
    """
    Display a list of active sales.
    
    URL: /sales/
    Template: sales/sale_list.html
    
    Filters:
        - search: Customer name.
        - status: Payment status (PAID/UNPAID).
    """
    model = Sale
    template_name = 'sales/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 50
    
    def get_queryset(self):
        """Apply filters to the default queryset (which already excludes deleted items)."""
        queryset = Sale.objects.all()
        
        # Filtering
        customer = self.request.GET.get('search')
        if customer:
            queryset = queryset.filter(customer_name__icontains=customer)
            
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(payment_status=status)
            
        return queryset


class SaleCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new Sale.
    
    URL: /sales/add/
    Form: SaleForm
    """
    model = Sale
    form_class = SaleForm
    template_name = 'sales/sale_form.html'
    success_url = reverse_lazy('sales:list')


class SaleDetailView(LoginRequiredMixin, DetailView):
    """
    View sale details, including payment history and audit logs.
    
    URL: /sales/<pk>/
    """
    model = Sale
    template_name = 'sales/sale_detail.html'
    context_object_name = 'sale'


class SaleUpdateView(LoginRequiredMixin, UpdateView):
    """
    Evaluate and update a sale.
    
    URL: /sales/<pk>/edit/
    """
    model = Sale
    form_class = SaleForm
    template_name = 'sales/sale_form.html'
    
    def get_success_url(self):
        return reverse_lazy('sales:detail', kwargs={'pk': self.object.pk})


class SaleArchiveView(LoginRequiredMixin, FormView):
    """
    Soft-delete a sale.
    
    Step:
        1. User clicks delete.
        2. Form prompts for 'Reason'.
        3. On valid submit, calls sale.soft_delete().
    """
    form_class = ArchiveSaleForm
    template_name = 'sales/sale_archive.html'
    
    def setup(self, request, *args, **kwargs):
        """Initialize the sale object from URL pk."""
        super().setup(request, *args, **kwargs)
        self.sale = get_object_or_404(Sale, pk=kwargs['pk'])
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sale'] = self.sale
        return context
        
    def form_valid(self, form):
        """Execute soft delete logic."""
        reason = form.cleaned_data['reason']
        self.sale.soft_delete(self.request.user, reason)
        messages.success(self.request, f"Sale #{self.sale.pk} archived successfully.")
        return redirect('sales:list')


class SaleArchivedListView(LoginRequiredMixin, ListView):
    """
    Separate list view for archived (deleted) sales.
    
    URL: /sales/archived/
    """
    model = Sale
    template_name = 'sales/sale_archived_list.html'
    context_object_name = 'sales'
    paginate_by = 50
    
    def get_queryset(self):
        """Use the custom 'archived' manager."""
        return Sale.archived.all().order_by('-deleted_at')


class RestoreSaleView(LoginRequiredMixin, View):
    """
    Action to restore a soft-deleted sale.
    
    Method: POST only.
    """
    def post(self, request, pk):
        sale = get_object_or_404(Sale.archived.all(), pk=pk)
        sale.restore()
        messages.success(request, f"Sale #{sale.pk} restored successfully.")
        return redirect('sales:detail', pk=sale.pk)


class PaymentCreateView(LoginRequiredMixin, CreateView):
    """
    HTMX-compatible view to add a payment.
    
    URL Pattern: /sales/<pk>/payments/add/
    Template: sales/partials/payment_form.html (modal dialog)
    
    Features:
        - Validates PaymentForm (ensures payment doesn't exceed balance due).
        - Passes 'sale' context to template for display of sale details.
        - On success, returns payment_list.html partial for HTMX swap.
        - Frontend confirmation dialog before submission.
    
    Methods:
        setup: Loads the parent Sale instance from URL.
        get_form_kwargs: Passes sale to form for validation.
        get_context_data: Adds sale to template context.
        form_valid: Saves payment and returns updated payment list.
    """
    model = Payment
    form_class = PaymentForm
    template_name = 'sales/partials/payment_form.html'
    
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.sale = get_object_or_404(Sale, pk=kwargs['pk'])
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['sale'] = self.sale
        return kwargs
    
    def get_context_data(self, **kwargs):
        """Pass sale object to template for form display."""
        context = super().get_context_data(**kwargs)
        context['sale'] = self.sale
        return context
        
    def form_valid(self, form):
        payment = form.save(commit=False)
        payment.sale = self.sale
        payment.created_by = self.request.user
        payment.save()
        
        # Return updated payment list partial
        from django.template.loader import render_to_string
        return HttpResponse(
            render_to_string('sales/partials/payment_list.html', {'sale': self.sale})
        )
