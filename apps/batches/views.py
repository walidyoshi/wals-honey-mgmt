"""
Batch management views
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum, F
from .models import Batch
from .forms import BatchForm


class BatchListView(LoginRequiredMixin, ListView):
    """List all batches with filtering"""
    model = Batch
    template_name = 'batches/batch_list.html'
    context_object_name = 'batches'
    paginate_by = 25
    
    def get_queryset(self):
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
    """Register a new jerrycan batch"""
    model = Batch
    form_class = BatchForm
    template_name = 'batches/batch_form.html'
    success_url = reverse_lazy('batches:list')


class BatchDetailView(LoginRequiredMixin, DetailView):
    """View batch details and history"""
    model = Batch
    template_name = 'batches/batch_detail.html'
    context_object_name = 'batch'


class BatchUpdateView(LoginRequiredMixin, UpdateView):
    """Update batch details"""
    model = Batch
    form_class = BatchForm
    template_name = 'batches/batch_form.html'
    
    def get_success_url(self):
        return reverse_lazy('batches:detail', kwargs={'pk': self.object.pk})


class BatchDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a batch"""
    model = Batch
    template_name = 'batches/batch_confirm_delete.html'
    success_url = reverse_lazy('batches:list')


class BatchGroupSummaryView(LoginRequiredMixin, ListView):
    """View summary of all batches in a specific group"""
    model = Batch
    template_name = 'batches/group_summary.html'
    context_object_name = 'batches'
    
    def get_queryset(self):
        group_id = self.kwargs.get('group_id')
        return Batch.objects.filter(batch_id__endswith=group_id)
    
    def get_context_data(self, **kwargs):
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
