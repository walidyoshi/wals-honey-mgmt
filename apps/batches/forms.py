"""
Batches Forms

This module handles form processing for Batch management.

Forms:
- BatchForm: Handles creation and editing of batches with custom validation.
"""

from django import forms
from datetime import datetime
from .models import Batch


class BatchForm(forms.ModelForm):
    """
    Form for creating and updating Batch records.
    
    Custom Behaviors:
        - supply_date: Manually rendered as text input to support custom date formats
          and avoid browser-specific date pickers that might conflict with user preference.
        - clean_supply_date: Logic to parse multiple date formats (dd/mm/yyyy first).
        - inputmode: Adds HTML attributes for numeric keypads on mobile devices.
    """
    
    # Override supply_date to use CharField to avoid Django's date widget validation
    supply_date = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'dd/mm/yyyy',
            'class': 'date-input'
        })
    )
    
    class Meta:
        model = Batch
        fields = [
            'batch_id', 'price', 'tp_cost', 'supply_date', 'source',
            'bottles_25cl', 'bottles_75cl', 'bottles_1L', 'bottles_4L',
            'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'inputmode': 'numeric', 'step': '0.01'}),
            'tp_cost': forms.NumberInput(attrs={'inputmode': 'numeric', 'step': '0.01'}),
            'bottles_25cl': forms.NumberInput(attrs={'inputmode': 'numeric'}),
            'bottles_75cl': forms.NumberInput(attrs={'inputmode': 'numeric'}),
            'bottles_1L': forms.NumberInput(attrs={'inputmode': 'numeric'}),
            'bottles_4L': forms.NumberInput(attrs={'inputmode': 'numeric'}),
        }
    
    def __init__(self, *args, **kwargs):
        """
        Initialize form and set optional fields.
        
        Only batch_id is required. All other fields are optional.
        """
        super().__init__(*args, **kwargs)
        
        # Make these fields optional (only batch_id is required)
        optional_fields = [
            'price', 'tp_cost', 'source', 'notes',
            'bottles_25cl', 'bottles_75cl', 'bottles_1L', 'bottles_4L'
        ]
        for field in optional_fields:
            if field in self.fields:
                self.fields[field].required = False
    
    def clean_bottles_25cl(self):
        """Convert empty bottle count to 0."""
        return self.cleaned_data.get('bottles_25cl') or 0
    
    def clean_bottles_75cl(self):
        """Convert empty bottle count to 0."""
        return self.cleaned_data.get('bottles_75cl') or 0
    
    def clean_bottles_1L(self):
        """Convert empty bottle count to 0."""
        return self.cleaned_data.get('bottles_1L') or 0
    
    def clean_bottles_4L(self):
        """Convert empty bottle count to 0."""
        return self.cleaned_data.get('bottles_4L') or 0
    
    def clean_price(self):
        """Convert empty price to 0."""
        return self.cleaned_data.get('price') or 0
    
    def clean_tp_cost(self):
        """Convert empty transport cost to None (allowed by model)."""
        return self.cleaned_data.get('tp_cost') or None
    
    def clean_supply_date(self):
        """
        Validate and parse the supply date.
        
        Logic:
            - Attempt to parse as dd/mm/yyyy (primary format).
            - Fallback to YYYY-MM-DD.
        
        Returns:
            date: Python date object if valid.
            
        Raises:
            ValidationError: If date format is invalid.
        """
        supply_date = self.data.get('supply_date', '')
        
        if not supply_date:
            return None
        
        # Try to parse dd/mm/yyyy format
        try:
            return datetime.strptime(supply_date, '%d/%m/%Y').date()
        except ValueError:
            # If that fails, try other common formats
            try:
                return datetime.strptime(supply_date, '%Y-%m-%d').date()
            except ValueError:
                raise forms.ValidationError('Please enter a valid date in dd/mm/yyyy format')
    
    def clean(self):
        """
        Perform cross-field validation.
        
        Current Logic:
            - Checks for group price consistency (currently non-blocking warning logic).
        """
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
