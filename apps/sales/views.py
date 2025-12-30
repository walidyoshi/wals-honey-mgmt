"""
Sales management views
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
    """List all active sales with filters"""
    model = Sale
    template_name = 'sales/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Sale.objects.all()  # Manager excludes deleted by default
        
        # Filtering
        customer = self.request.GET.get('search')
        if customer:
            queryset = queryset.filter(customer_name__icontains=customer)
            
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(payment_status=status)
            
        return queryset


class SaleCreateView(LoginRequiredMixin, CreateView):
    """Record a new sale"""
    model = Sale
    form_class = SaleForm
    template_name = 'sales/sale_form.html'
    success_url = reverse_lazy('sales:list')


class SaleDetailView(LoginRequiredMixin, DetailView):
    """View sale details, payments and history"""
    model = Sale
    template_name = 'sales/sale_detail.html'
    context_object_name = 'sale'


class SaleUpdateView(LoginRequiredMixin, UpdateView):
    """Update sale details"""
    model = Sale
    form_class = SaleForm
    template_name = 'sales/sale_form.html'
    
    def get_success_url(self):
        return reverse_lazy('sales:detail', kwargs={'pk': self.object.pk})


class SaleArchiveView(LoginRequiredMixin, FormView):
    """Soft delete a sale"""
    form_class = ArchiveSaleForm
    template_name = 'sales/sale_archive.html'
    
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.sale = get_object_or_404(Sale, pk=kwargs['pk'])
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sale'] = self.sale
        return context
        
    def form_valid(self, form):
        reason = form.cleaned_data['reason']
        self.sale.soft_delete(self.request.user, reason)
        messages.success(self.request, f"Sale #{self.sale.pk} archived successfully.")
        return redirect('sales:list')


class SaleArchivedListView(LoginRequiredMixin, ListView):
    """List archived/deleted sales"""
    model = Sale
    template_name = 'sales/sale_archived_list.html'
    context_object_name = 'sales'
    paginate_by = 50
    
    def get_queryset(self):
        return Sale.archived.all().order_by('-deleted_at')


class RestoreSaleView(LoginRequiredMixin, View):
    """Restore an archived sale"""
    def post(self, request, pk):
        sale = get_object_or_404(Sale.archived.all(), pk=pk)
        sale.restore()
        messages.success(request, f"Sale #{sale.pk} restored successfully.")
        return redirect('sales:detail', pk=sale.pk)


class PaymentCreateView(LoginRequiredMixin, CreateView):
    """Add payment via HTMX modal"""
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
