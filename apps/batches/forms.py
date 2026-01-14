"""
Forms for batch management
"""

from django import forms
from .models import Batch


class BatchForm(forms.ModelForm):
    """Form for creating and updating batches"""
    
    class Meta:
        model = Batch
        fields = [
            'batch_id', 'price', 'tp_cost', 'supply_date', 'source',
            'bottles_25cl', 'bottles_75cl', 'bottles_1L', 'bottles_4L',
            'notes'
        ]
        widgets = {
            'supply_date': forms.DateInput(attrs={
                'type': 'text',
                'placeholder': 'dd/mm/yyyy',
                'class': 'date-input'
            }),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'inputmode': 'numeric', 'step': '0.01'}),
            'tp_cost': forms.NumberInput(attrs={'inputmode': 'numeric', 'step': '0.01'}),
            'bottles_25cl': forms.NumberInput(attrs={'inputmode': 'numeric'}),
            'bottles_75cl': forms.NumberInput(attrs={'inputmode': 'numeric'}),
            'bottles_1L': forms.NumberInput(attrs={'inputmode': 'numeric'}),
            'bottles_4L': forms.NumberInput(attrs={'inputmode': 'numeric'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        batch_id = cleaned_data.get('batch_id')
        
        # Helper to get group number
        if batch_id and len(batch_id) >= 3:
            group_number = batch_id[-3:]
            
            # Warn if price differs from other batches in same group
            # Note: This is a warning (non-blocking) validation in logic, 
            # but here we can just ensure valid data or raise simple errors.
            # Complex warnings usually require UI feedback not standard form errors.
            pass
            
        return cleaned_data
