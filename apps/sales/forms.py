"""
Sales Forms

This module handles Sales and Payment data entry forms.

Forms:
- SaleForm: Main transaction form with HTMX autocomplete.
- PaymentForm: For adding portions of payment with validation.
- ArchiveSaleForm: Captures reason for soft-deleting a sale.
"""

from django import forms
from .models import Sale, Payment
from apps.batches.models import Batch


class SaleForm(forms.ModelForm):
    """
    Form for creating/updating a Sale.
    
    Features:
        - HTMX Autocomplete: 'customer_name' field polls /customers/autocomplete/
        - Dynamic Batch Filtering: Shows available batches.
        - Numeric Keypads: Uses 'inputmode' for mobile friendliness.
    """
    
    class Meta:
        model = Sale
        fields = [
            'customer_name', 'bottle_type', 'unit_price', 
            'quantity', 'batch', 'payment_status', 
            'is_wholesale', 'notes'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'hx-get': '/customers/autocomplete/',
                'hx-trigger': 'keyup changed delay:500ms',
                'hx-target': '#customer-results',
                'autocomplete': 'off'
            }),
            'notes': forms.Textarea(attrs={'rows': 2}),
            'unit_price': forms.NumberInput(attrs={'inputmode': 'numeric', 'step': '0.01'}),
            'quantity': forms.NumberInput(attrs={'inputmode': 'numeric'}),
        }
    
    def __init__(self, *args, **kwargs):
        """Initialize form and filter batch queryset."""
        super().__init__(*args, **kwargs)
        # Only show batches with stock available (simplified logic)
        self.fields['batch'].queryset = Batch.objects.all().order_by('-supply_date')


class PaymentForm(forms.ModelForm):
    """
    Form for recording a payment.
    
    Validation:
        - Ensures payment amount does not exceed the remaining balance on the sale.
    """
    
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
            'amount': forms.NumberInput(attrs={'inputmode': 'numeric', 'step': '0.01'}),
        }
    
    def __init__(self, sale=None, *args, **kwargs):
        """
        Initialize with the parent Sale instance.
        
        Args:
            sale (Sale): The sale this payment belongs to.
        """
        self.sale = sale
        super().__init__(*args, **kwargs)
        
    def clean_amount(self):
        """
        Validate that the payment amount is not greater than what is owed.
        
        Returns:
            Decimal: Validated amount.
            
        Raises:
            ValidationError: If amount > amount_due.
        """
        amount = self.cleaned_data['amount']
        if self.sale:
            if amount > self.sale.amount_due:
                raise forms.ValidationError(f"Amount exceeds balance due (₦{self.sale.amount_due})")
        return amount


class ArchiveSaleForm(forms.Form):
    """Simple form to enforce providing a reason when deleting a sale."""
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Reason for deletion required'}),
        required=True
    )
