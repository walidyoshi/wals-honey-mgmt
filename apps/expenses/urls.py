"""
Expense URL Configuration
"""

from django.urls import path
from .views import (
    ExpenseListView, ExpenseCreateView, ExpenseDetailView, 
    ExpenseUpdateView, ExpenseArchiveView, ExpenseArchivedListView,
    RestoreExpenseView
)

app_name = 'expenses'

urlpatterns = [
    path('', ExpenseListView.as_view(), name='list'),
    path('archived/', ExpenseArchivedListView.as_view(), name='archived_list'),
    path('add/', ExpenseCreateView.as_view(), name='create'),
    path('<int:pk>/', ExpenseDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', ExpenseUpdateView.as_view(), name='update'),
    path('<int:pk>/archive/', ExpenseArchiveView.as_view(), name='archive'),
    path('<int:pk>/restore/', RestoreExpenseView.as_view(), name='restore'),
]
