"""
Forms for expense management
"""

from django import forms
from datetime import datetime
from .models import Expense


class ExpenseForm(forms.ModelForm):
    """Form for adding/updating expenses"""
    
    # Override expense_date to use CharField to avoid Django's date widget validation
    expense_date = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'dd/mm/yyyy',
            'class': 'date-input'
        })
    )
    
    class Meta:
        model = Expense
        fields = ['item', 'cost', 'expense_date', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'cost': forms.NumberInput(attrs={'inputmode': 'numeric', 'step': '0.01'}),
        }
    
    def clean_expense_date(self):
        """Parse dd/mm/yyyy format to date object"""
        expense_date = self.data.get('expense_date', '')
        
        if not expense_date:
            raise forms.ValidationError('Expense date is required')
        
        # Try to parse dd/mm/yyyy format
        try:
            return datetime.strptime(expense_date, '%d/%m/%Y').date()
        except ValueError:
            # If that fails, try other common formats
            try:
                return datetime.strptime(expense_date, '%Y-%m-%d').date()
            except ValueError:
                raise forms.ValidationError('Please enter a valid date in dd/mm/yyyy format')



class ArchiveExpenseForm(forms.Form):
    """Form for soft deleting/archiving an expense"""
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Reason for deletion required'}),
        required=True
    )
