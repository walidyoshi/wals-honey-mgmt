"""
Sales and Payment models
"""

from django.db import models
from django.db.models import Sum, Q
from django.utils import timezone
from apps.core.models import UserTrackingModel


class SaleManager(models.Manager):
    """Custom manager to exclude deleted sales by default"""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class ArchivedSaleManager(models.Manager):
    """Manager to find deleted sales"""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=True)


class Sale(UserTrackingModel):
    """Sales transaction record with soft delete support"""
    
    BOTTLE_CHOICES = [
        ('25CL', '25cl'),
        ('75CL', '75cl'),
        ('1L', '1 Litre'),
        ('4L', '4 Litres'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PAID', 'Fully Paid'),
        ('UNPAID', 'Unpaid'),
        ('PARTIAL', 'Partial Payment'),
    ]
    
    # Customer information
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales'
    )
    customer_name = models.CharField(
        max_length=200,
        help_text="Used if customer not in system"
    )
    
    # Sale details
    bottle_type = models.CharField(max_length=10, choices=BOTTLE_CHOICES)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    batch = models.ForeignKey(
        'batches.Batch',
        on_delete=models.PROTECT,
        related_name='sales'
    )
    
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='UNPAID'
    )
    
    is_wholesale = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    sale_date = models.DateField(auto_now_add=True)
    sale_time = models.TimeField(auto_now_add=True)
    
    # Soft delete fields
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_reason = models.TextField(blank=True)
    deleted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='sales_deleted',
        null=True,
        blank=True
    )
    
    # Managers
    objects = SaleManager()
    archived = ArchivedSaleManager()
    all_objects = models.Manager()  # Access to everything
    
    class Meta:
        ordering = ['-sale_date', '-sale_time']
    
    def __str__(self):
        return f"Sale #{self.id} - {self.customer_name}"
    
    @property
    def amount_paid(self):
        """Calculate total paid from payment history"""
        total = self.payments.aggregate(Sum('amount'))['amount__sum']
        return total or 0
    
    @property
    def amount_due(self):
        """Remaining balance"""
        return self.total_price - self.amount_paid
    
    def update_payment_status(self):
        """Auto-update payment status based on payments"""
        paid = self.amount_paid
        if paid == 0:
            self.payment_status = 'UNPAID'
        elif paid >= self.total_price:
            self.payment_status = 'PAID'
        else:
            self.payment_status = 'PARTIAL'
        self.save()
    
    def soft_delete(self, user, reason):
        """Perform soft delete"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.deleted_reason = reason
        self.save()

    def restore(self):
        """Restore deleted sale"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.deleted_reason = ""
        self.save()
    
    def save(self, *args, **kwargs):
        # Auto-calculate total_price
        if self.unit_price and self.quantity:
            self.total_price = self.unit_price * self.quantity
        
        # Auto-create customer if needed
        if self.customer_name and not self.customer:
            from apps.customers.models import Customer
            
            # We need to find or create customer
            # If we're updating existing sale, we use modified_by user
            # If new sale, we might not have user yet if not set explicitly
            # The UserTrackingMiddleware handles setting self.modified_by on save
            # But here we are BEFORE save, so we need to be careful
            
            # Since get_current_user exists in middleware
            # We can use it here as well for the customer creation
            from apps.core.middleware import get_current_user
            current_user = get_current_user()
            
            defaults = {}
            if current_user and current_user.is_authenticated:
                defaults['created_by'] = current_user
                defaults['modified_by'] = current_user
                
            customer, created = Customer.objects.get_or_create(
                name=self.customer_name,
                defaults=defaults
            )
            self.customer = customer
        
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Payment transaction history for sales"""
    
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('TRANSFER', 'Bank Transfer'),
        ('POS', 'POS'),
        ('CHEQUE', 'Cheque'),
    ]
    
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES,
        default='CASH'
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT
    )
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"₦{self.amount} for Sale #{self.sale.id}"
    
    def save(self, *args, **kwargs):
        # Auto-assign created_by if not set
        if not self.pk and not hasattr(self, 'created_by'):
             from apps.core.middleware import get_current_user
             user = get_current_user()
             if user and user.is_authenticated:
                 self.created_by = user
        super().save(*args, **kwargs)
