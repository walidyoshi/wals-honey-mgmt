"""
Expense management views
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView, View
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Expense
from .forms import ExpenseForm, ArchiveExpenseForm


class ExpenseListView(LoginRequiredMixin, ListView):
    """List all active expenses with filtering"""
    model = Expense
    template_name = 'expenses/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Expense.objects.all()  # Default manager excludes deleted
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(item__icontains=search)
            
        # Date range
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(expense_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(expense_date__lte=date_to)
            
        return queryset


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    """Add a new expense"""
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expenses:list')


class ExpenseDetailView(LoginRequiredMixin, DetailView):
    """View expense details"""
    model = Expense
    template_name = 'expenses/expense_detail.html'
    context_object_name = 'expense'


class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    """Update expense details"""
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expenses:list')


class ExpenseArchiveView(LoginRequiredMixin, FormView):
    """Soft delete an expense"""
    form_class = ArchiveExpenseForm
    template_name = 'expenses/expense_archive.html'
    
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.expense = get_object_or_404(Expense, pk=kwargs['pk'])
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expense'] = self.expense
        return context
        
    def form_valid(self, form):
        reason = form.cleaned_data['reason']
        self.expense.soft_delete(self.request.user, reason)
        messages.success(self.request, f"Expense '{self.expense.item}' archived successfully.")
        return redirect('expenses:list')


class ExpenseArchivedListView(LoginRequiredMixin, ListView):
    """List archived/deleted expenses"""
    model = Expense
    template_name = 'expenses/expense_archived_list.html'
    context_object_name = 'expenses'
    paginate_by = 50
    
    def get_queryset(self):
        return Expense.archived.all().order_by('-deleted_at')


class RestoreExpenseView(LoginRequiredMixin, View):
    """Restore an archived expense"""
    def post(self, request, pk):
        expense = get_object_or_404(Expense.archived.all(), pk=pk)
        expense.restore()
        messages.success(request, f"Expense '{expense.item}' restored successfully.")
        return redirect('expenses:detail', pk=expense.pk)
