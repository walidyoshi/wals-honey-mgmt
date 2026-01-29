"""
URL Configuration for honey_mgmt project
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('', include('apps.sales.urls')),  # Sales as home/dashboard
    path('batches/', include('apps.batches.urls')),
    path('expenses/', include('apps.expenses.urls')),
    path('customers/', include('apps.customers.urls')),
    path('statistics/', include('apps.reports.urls')),
]
