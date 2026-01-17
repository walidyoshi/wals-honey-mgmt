"""
Expenses Views

This module manages the viewing, creating, and editing of expenses.

Views:
- ExpenseListView: Filterable list of expenses.
- ExpenseCreateView: Add new expense.
- ExpenseArchiveView: Soft-delete an expense.
- RestoreExpenseView: Undo soft-delete.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView, View
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Expense
from .forms import ExpenseForm, ArchiveExpenseForm


class ExpenseListView(LoginRequiredMixin, ListView):
    """
    Display list of active expenses.
    
    URL: /expenses/
    Template: expenses/expense_list.html
    
    Filters (GET params):
        - search: Text search on 'item' description.
        - date_from, date_to: Range filtering on 'expense_date'.
    """
    model = Expense
    template_name = 'expenses/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 50
    
    def get_queryset(self):
        """
        Return filtered queryset.
        
        Logic:
            - Applies search filter if present.
            - Applies date range filter if present.
        """
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
    """
    Add a new expense.
    
    URL: /expenses/add/
    Form: ExpenseForm
    """
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expenses:list')


class ExpenseDetailView(LoginRequiredMixin, DetailView):
    """
    View expense details.
    
    URL: /expenses/<pk>/
    """
    model = Expense
    template_name = 'expenses/expense_detail.html'
    context_object_name = 'expense'


class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing expense.
    
    URL: /expenses/<pk>/edit/
    Form: ExpenseForm
    """
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expenses:list')


class ExpenseArchiveView(LoginRequiredMixin, FormView):
    """
    Soft-delete an expense.
    
    URL: /expenses/<pk>/delete/
    """
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
    """
    List soft-deleted expenses.
    
    URL: /expenses/archived/
    """
    model = Expense
    template_name = 'expenses/expense_archived_list.html'
    context_object_name = 'expenses'
    paginate_by = 50
    
    def get_queryset(self):
        return Expense.archived.all().order_by('-deleted_at')


class RestoreExpenseView(LoginRequiredMixin, View):
    """
    Restore a soft-deleted expense.
    
    Method: POST
    """
    def post(self, request, pk):
        expense = get_object_or_404(Expense.archived.all(), pk=pk)
        expense.restore()
        messages.success(request, f"Expense '{expense.item}' restored successfully.")
        return redirect('expenses:detail', pk=expense.pk)
