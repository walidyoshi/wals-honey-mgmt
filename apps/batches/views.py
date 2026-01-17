"""
Batches Views

This module provides views for managing honey batches.

Views:
- BatchListView: Browse inventory.
- BatchCreate/Update/DeleteView: CRUD operations.
- BatchGroupSummaryView: Aggregated insights for a specific group of batches (e.g., G02).
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum, F
from .models import Batch
from .forms import BatchForm


class BatchListView(LoginRequiredMixin, ListView):
    """
    Display list of all batches with filtering capabilities.
    
    URL: /batches/
    Template: batches/batch_list.html
    
    Filters (GET params):
        - search: Matches against batch_id.
        - group: Matches batches ending with specific string (group ID).
    """
    model = Batch
    template_name = 'batches/batch_list.html'
    context_object_name = 'batches'
    paginate_by = 25
    
    def get_queryset(self):
        """
        Return filtered queryset based on GET parameters.
        
        Returns:
            QuerySet: Filtered Batches.
        """
        queryset = super().get_queryset()
        
        # Filtering
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(batch_id__icontains=search)
            
        group = self.request.GET.get('group')
        if group:
            queryset = queryset.filter(batch_id__endswith=group)
            
        return queryset


class BatchCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new Batch.
    
    URL: /batches/add/
    Form: BatchForm
    """
    model = Batch
    form_class = BatchForm
    template_name = 'batches/batch_form.html'
    success_url = reverse_lazy('batches:list')


class BatchDetailView(LoginRequiredMixin, DetailView):
    """
    View detailed information about a single batch.
    
    URL: /batches/<pk>/
    """
    model = Batch
    template_name = 'batches/batch_detail.html'
    context_object_name = 'batch'


class BatchUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing Batch.
    
    URL: /batches/<pk>/edit/
    Form: BatchForm
    """
    model = Batch
    form_class = BatchForm
    template_name = 'batches/batch_form.html'
    
    def get_success_url(self):
        """Redirect to detail page after update."""
        return reverse_lazy('batches:detail', kwargs={'pk': self.object.pk})


class BatchDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete a Batch.
    
    URL: /batches/<pk>/delete/
    Template: batches/batch_confirm_delete.html
    """
    model = Batch
    template_name = 'batches/batch_confirm_delete.html'
    success_url = reverse_lazy('batches:list')


class BatchGroupSummaryView(LoginRequiredMixin, ListView):
    """
    Display a summary for a group of batches (e.g., all batches in G02).
    
    URL: /batches/group/<group_id>/
    Template: batches/group_summary.html
    
    Aggregations:
        - Total Cost (Price + Transport).
        - Total Bottles by size.
    """
    model = Batch
    template_name = 'batches/group_summary.html'
    context_object_name = 'batches'
    
    def get_queryset(self):
        """Fetch batches matching the group ID from URL."""
        group_id = self.kwargs.get('group_id')
        return Batch.objects.filter(batch_id__endswith=group_id)
    
    def get_context_data(self, **kwargs):
        """
        Calculate financial and production aggregates.
        
        Returns:
            dict: Context including 'total_cost' and 'total_bottles' (dict of sizes).
        """
        context = super().get_context_data(**kwargs)
        batches = self.get_queryset()
        
        context['group_id'] = self.kwargs.get('group_id')
        context['total_cost'] = batches.aggregate(
            total=Sum('price') + Sum(F('tp_cost'))
        )['total'] or 0
        
        # Aggregate bottle counts
        context['total_bottles'] = batches.aggregate(
            b25=Sum('bottles_25cl'),
            b75=Sum('bottles_75cl'),
            b1=Sum('bottles_1L'),
            b4=Sum('bottles_4L')
        )
        
        return context
