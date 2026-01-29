"""
Reports URL Configuration
"""

from django.urls import path
from .views import StatisticsView

app_name = 'reports'

urlpatterns = [
    path('', StatisticsView.as_view(), name='statistics'),
]
