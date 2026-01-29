"""
Reports Views

This module provides financial summary statistics with date filtering.

Views:
- StatisticsView: Dashboard showing totals for sales, expenses, and batch costs.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, F, Q
from django.db.models.functions import Coalesce
from django.views.generic import TemplateView

from apps.sales.models import Sale, Payment
from apps.expenses.models import Expense
from apps.batches.models import Batch


class StatisticsView(LoginRequiredMixin, TemplateView):
    """
    Financial statistics dashboard with date filtering.
    
    Displays:
        - Total Sales (sum of sale totals)
        - Total Expenses
        - Total Batch Costs (purchase + transport)
        - Sales Collected vs Pending breakdown
    
    Filters:
        - Quick presets: this_week, last_week, this_month, last_month
        - Custom date range: date_from, date_to
    """
    template_name = 'reports/statistics.html'
    
    def get_date_range(self):
        """
        Parse date filter from request and return (start_date, end_date) tuple.
        
        Returns:
            tuple: (date_from, date_to, preset_name)
        """
        today = date.today()
        preset = self.request.GET.get('preset', '')
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')
        
        if preset == 'this_week':
            # Monday of this week
            start = today - timedelta(days=today.weekday())
            return (start, today, 'this_week')
        
        elif preset == 'last_week':
            # Monday to Sunday of last week
            start = today - timedelta(days=today.weekday() + 7)
            end = start + timedelta(days=6)
            return (start, end, 'last_week')
        
        elif preset == 'this_month':
            start = today.replace(day=1)
            return (start, today, 'this_month')
        
        elif preset == 'last_month':
            # First day of last month
            first_of_this_month = today.replace(day=1)
            last_of_prev_month = first_of_this_month - timedelta(days=1)
            start = last_of_prev_month.replace(day=1)
            return (start, last_of_prev_month, 'last_month')
        
        elif date_from and date_to:
            try:
                from datetime import datetime
                # Try dd/mm/yyyy format first
                try:
                    start = datetime.strptime(date_from, '%d/%m/%Y').date()
                    end = datetime.strptime(date_to, '%d/%m/%Y').date()
                except ValueError:
                    # Fallback to yyyy-mm-dd
                    start = datetime.strptime(date_from, '%Y-%m-%d').date()
                    end = datetime.strptime(date_to, '%Y-%m-%d').date()
                return (start, end, 'custom')
            except ValueError:
                pass
        
        # Default: All time (no filter)
        return (None, None, 'all')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        date_from, date_to, preset = self.get_date_range()
        
        # Base querysets (excluding soft-deleted)
        sales_qs = Sale.objects.all()
        expenses_qs = Expense.objects.all()
        batches_qs = Batch.objects.all()
        
        # Apply date filters
        if date_from and date_to:
            sales_qs = sales_qs.filter(sale_date__gte=date_from, sale_date__lte=date_to)
            expenses_qs = expenses_qs.filter(expense_date__gte=date_from, expense_date__lte=date_to)
            batches_qs = batches_qs.filter(supply_date__gte=date_from, supply_date__lte=date_to)
        
        # Calculate totals
        total_sales = sales_qs.aggregate(
            total=Coalesce(Sum('total_price'), Decimal('0'))
        )['total']
        
        total_expenses = expenses_qs.aggregate(
            total=Coalesce(Sum('cost'), Decimal('0'))
        )['total']
        
        # Batch cost = price + tp_cost (handle nulls)
        total_batch_cost = batches_qs.aggregate(
            total=Coalesce(
                Sum(Coalesce(F('price'), Decimal('0')) + Coalesce(F('tp_cost'), Decimal('0'))),
                Decimal('0')
            )
        )['total']
        
        # Sales collected (sum of payments for sales in date range)
        if date_from and date_to:
            payments_qs = Payment.objects.filter(
                sale__in=sales_qs
            )
        else:
            payments_qs = Payment.objects.all()
        
        sales_collected = payments_qs.aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']
        
        # Sales pending = total sales - collected
        sales_pending = total_sales - sales_collected
        
        # Context data
        context.update({
            'total_sales': total_sales,
            'total_expenses': total_expenses,
            'total_batch_cost': total_batch_cost,
            'sales_collected': sales_collected,
            'sales_pending': sales_pending,
            'date_from': date_from,
            'date_to': date_to,
            'current_preset': preset,
            'date_from_str': self.request.GET.get('date_from', ''),
            'date_to_str': self.request.GET.get('date_to', ''),
        })
        
        return context
