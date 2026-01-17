"""
Sales Models

This module handles Sales transactions, Payments, and logical status updates.

Business Logic:
- A Sale represents a transaction with a Customer for a specific quantity of honey from a Batch.
- Sales have a computed 'payment_status' (UNPAID, PARTIAL, PAID) based on associated Payments.
- Sales can be 'soft-deleted' (archived) to preserve audit trails while hiding them from main reports.
- Customers can be auto-created during sale creation if they don't exist.

Models:
- Sale: The transaction header.
- Payment: Individual payments against a Sale.
"""

from django.db import models
from django.db.models import Sum, Q
from django.utils import timezone
from apps.core.models import UserTrackingModel


class SaleManager(models.Manager):
    """
    Default manager for Sale model.
    
    Behavior:
        Excludes soft-deleted sales from standard queries to prevent them from
        affecting reports and lists.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class ArchivedSaleManager(models.Manager):
    """
    Manager to retrieve only soft-deleted sales.
    
    Usage:
        Sale.archived.all()
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=True)


class Sale(UserTrackingModel):
    """
    Represents a sales transaction with a customer.
    
    Attributes:
        customer (Customer): Link to existing Customer (optional if just starting).
        customer_name (CharField): Name snapshot.
        bottle_type (CharField): Size of container sold (25CL, 75CL, etc.).
        unit_price (DecimalField): Price per unit.
        quantity (int): Number of units.
        total_price (DecimalField): Auto-calculated (unit_price * quantity).
        batch (Batch): Inventory source.
        payment_status (CharField): UNPAID, PARTIAL, or PAID.
        is_wholesale (bool): Flag for bulk pricing/logic.
        
        is_deleted (bool): Soft-delete flag.
        deleted_at (DateTimeField): When it was deleted.
        deleted_reason (TextField): Why it was deleted.
    
    Computed Properties:
        amount_paid: Sum of all related payments.
        amount_due: total_price - amount_paid.
    """
    
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
    all_objects = models.Manager()  # Access to everything (active + deleted)
    
    class Meta:
        ordering = ['-sale_date', '-sale_time']
    
    def __str__(self):
        return f"Sale #{self.id} - {self.customer_name}"
    
    @property
    def amount_paid(self):
        """
        Calculate the total amount paid so far.
        
        Returns:
            Decimal: Sum of all related Payment records.
        """
        total = self.payments.aggregate(Sum('amount'))['amount__sum']
        return total or 0
    
    @property
    def amount_due(self):
        """
        Calculate remaining balance.
        
        Returns:
            Decimal: Total Price - Amount Paid.
        """
        return self.total_price - self.amount_paid
    
    def update_payment_status(self):
        """
        Recalculate and update 'payment_status' based on current payments.
        
        Logic:
            - If paid == 0 -> UNPAID
            - If paid >= total -> PAID
            - Else -> PARTIAL
        """
        paid = self.amount_paid
        if paid == 0:
            self.payment_status = 'UNPAID'
        elif paid >= self.total_price:
            self.payment_status = 'PAID'
        else:
            self.payment_status = 'PARTIAL'
        self.save()
    
    def soft_delete(self, user, reason):
        """
        Mark sale as deleted without removing from database.
        
        Args:
            user (User): The admin performing the deletion.
            reason (str): Justification for deletion.
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.deleted_reason = reason
        self.save()

    def restore(self):
        """Undo soft-delete and restore to active state."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.deleted_reason = ""
        self.save()
    
    def save(self, *args, **kwargs):
        """
        Save the sale with business logic hooks.
        
        Hooks:
            1. Auto-calculates total_price (unit_price * quantity).
            2. Auto-creates Customer if 'customer_name' is provided but 'customer' FK is null.
        """
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
    """
    Record of a payment made against a Sale.
    
    Attributes:
        sale (Sale): The parent transaction.
        amount (Decimal): The amount paid.
        payment_method (str): CASH, TRANSFER, POS, etc.
        payment_date (DateTimeField): When it happened.
        created_by (User): Who recorded it.
    
    Signals:
        Triggers 'update_sale_payment_status' on save/delete.
    """
    
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
        """Auto-assign currently logged-in user to 'created_by'."""
        if not self.pk and not hasattr(self, 'created_by'):
             from apps.core.middleware import get_current_user
             user = get_current_user()
             if user and user.is_authenticated:
                 self.created_by = user
        super().save(*args, **kwargs)
