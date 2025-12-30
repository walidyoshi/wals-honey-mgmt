"""
Batch URL Configuration
"""

from django.urls import path
from .views import (
    BatchListView, BatchCreateView, BatchDetailView, 
    BatchUpdateView, BatchDeleteView, BatchGroupSummaryView
)

app_name = 'batches'

urlpatterns = [
    path('', BatchListView.as_view(), name='list'),
    path('add/', BatchCreateView.as_view(), name='create'),
    path('<int:pk>/', BatchDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', BatchUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', BatchDeleteView.as_view(), name='delete'),
    path('group/<str:group_id>/', BatchGroupSummaryView.as_view(), name='group_summary'),
]
