"""
Admin configuration for sales app
"""

from django.contrib import admin
from .models import Sale, Payment


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['created_by', 'payment_date']
    can_delete = False


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'total_price', 'payment_status', 'is_deleted', 'sale_date']
    list_filter = ['payment_status', 'is_deleted', 'sale_date', 'is_wholesale']
    search_fields = ['customer_name', 'notes']
    readonly_fields = ['created_at', 'modified_at', 'created_by', 'modified_by', 'deleted_at', 'deleted_by']
    inlines = [PaymentInline]
    
    def get_queryset(self, request):
        # Show all sales including deleted ones in admin
        return self.model.all_objects.all()


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'sale', 'amount', 'payment_method', 'payment_date', 'created_by']
    list_filter = ['payment_method', 'payment_date']
    readonly_fields = ['payment_date', 'created_by']
