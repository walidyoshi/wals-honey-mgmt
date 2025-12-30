"""
Sales URL Configuration
"""

from django.urls import path
from .views import (
    SaleListView, SaleCreateView, SaleDetailView, 
    SaleUpdateView, SaleArchiveView, SaleArchivedListView,
    RestoreSaleView, PaymentCreateView
)

app_name = 'sales'

urlpatterns = [
    path('', SaleListView.as_view(), name='list'),
    path('archived/', SaleArchivedListView.as_view(), name='archived_list'),
    path('add/', SaleCreateView.as_view(), name='create'),
    path('<int:pk>/', SaleDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', SaleUpdateView.as_view(), name='update'),
    path('<int:pk>/archive/', SaleArchiveView.as_view(), name='archive'),
    path('<int:pk>/restore/', RestoreSaleView.as_view(), name='restore'),
    path('<int:pk>/payments/add/', PaymentCreateView.as_view(), name='add_payment'),
]
