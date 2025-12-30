"""
Forms for sales management
"""

from django import forms
from .models import Sale, Payment
from apps.batches.models import Batch


class SaleForm(forms.ModelForm):
    """Form for recording a new sale"""
    
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
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show batches with stock available (simplified logic)
        # In a real app we'd filter this more strictly based on bottle counts
        self.fields['batch'].queryset = Batch.objects.all().order_by('-supply_date')


class PaymentForm(forms.ModelForm):
    """Form for adding payments"""
    
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, sale=None, *args, **kwargs):
        self.sale = sale
        super().__init__(*args, **kwargs)
        
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if self.sale:
            if amount > self.sale.amount_due:
                raise forms.ValidationError(f"Amount exceeds balance due (₦{self.sale.amount_due})")
        return amount


class ArchiveSaleForm(forms.Form):
    """Form for soft deleting/archiving a sale"""
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Reason for deletion required'}),
        required=True
    )
