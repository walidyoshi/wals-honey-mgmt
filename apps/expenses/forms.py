"""
Forms for expense management
"""

from django import forms
from .models import Expense


class ExpenseForm(forms.ModelForm):
    """Form for adding/updating expenses"""
    
    class Meta:
        model = Expense
        fields = ['item', 'cost', 'expense_date', 'notes']
        widgets = {
            'expense_date': forms.DateInput(attrs={
                'type': 'text',
                'placeholder': 'dd/mm/yyyy',
                'class': 'date-input'
            }),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'cost': forms.NumberInput(attrs={'inputmode': 'numeric', 'step': '0.01'}),
        }


class ArchiveExpenseForm(forms.Form):
    """Form for soft deleting/archiving an expense"""
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Reason for deletion required'}),
        required=True
    )
