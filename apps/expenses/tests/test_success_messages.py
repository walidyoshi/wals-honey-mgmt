"""
Unit Tests for Expense Success Messages

This module provides comprehensive test coverage for success messages
displayed after expense create/update operations.

Test Categories:
1. Expense create success messages
2. Expense update success messages
3. Edge cases (special characters, long text, concurrent operations)
"""

from decimal import Decimal
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from apps.expenses.models import Expense

User = get_user_model()


# =============================================================================
# EXPENSE SUCCESS MESSAGE TESTS
# =============================================================================

class ExpenseCreateSuccessMessageTests(TestCase):
    """Test success messages for expense creation."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test user."""
        cls.user = User.objects.create_user(
            email='expensecreate@example.com',
            password='testpass123',
            first_name='Expense',
            last_name='Creator'
        )
    
    def setUp(self):
        """Set up client."""
        self.client = Client()
        self.client.login(email='expensecreate@example.com', password='testpass123')
    
    def test_success_message_on_expense_create(self):
        """Test that success message is shown after creating an expense."""
        response = self.client.post(reverse('expenses:create'), {
            'item': 'Office Supplies',
            'cost': '5000',
            'expense_date': '15/01/2026'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Expense 'Office Supplies' created successfully.")
        self.assertEqual(messages[0].tags, 'success')
    
    def test_success_message_includes_item_name(self):
        """Test that success message includes the expense item name."""
        response = self.client.post(reverse('expenses:create'), {
            'item': 'Transportation',
            'cost': '3000',
            'expense_date': '10/01/2026'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('Transportation', str(messages[0]))
        self.assertIn('created successfully', str(messages[0]))
    
    def test_success_message_with_full_form_data(self):
        """Test success message when creating expense with all fields."""
        response = self.client.post(reverse('expenses:create'), {
            'item': 'Complete Expense',
            'cost': '25000.50',
            'expense_date': '20/01/2026',
            'notes': 'Detailed notes about the expense'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('Complete Expense', str(messages[0]))
        self.assertIn('created successfully', str(messages[0]))
    
    def test_no_message_on_invalid_form(self):
        """Test that no success message is shown on form validation error."""
        response = self.client.post(reverse('expenses:create'), {
            # Missing required fields
            'notes': 'Just notes'
        })
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)
    
    def test_success_message_with_special_characters_in_item(self):
        """Test success message with special characters in item name."""
        response = self.client.post(reverse('expenses:create'), {
            'item': "John's Repairs & Co. <Ltd>",
            'cost': '10000',
            'expense_date': '15/01/2026'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("John's Repairs & Co. <Ltd>", str(messages[0]))
    
    def test_success_message_with_unicode_in_item(self):
        """Test success message with unicode characters."""
        response = self.client.post(reverse('expenses:create'), {
            'item': 'Équipement de bureau',
            'cost': '7500',
            'expense_date': '15/01/2026'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('Équipement de bureau', str(messages[0]))
    
    def test_message_appears_on_list_page_after_redirect(self):
        """Test that message appears on list page after successful create."""
        response = self.client.post(reverse('expenses:create'), {
            'item': 'Redirect Test Expense',
            'cost': '4500',
            'expense_date': '15/01/2026'
        }, follow=True)
        
        # Should redirect to list page
        self.assertTemplateUsed(response, 'expenses/expense_list.html')
        
        # Message should be in response
        self.assertContains(response, 'Redirect Test Expense')
        self.assertContains(response, 'created successfully')


class ExpenseUpdateSuccessMessageTests(TestCase):
    """Test success messages for expense updates."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test user."""
        cls.user = User.objects.create_user(
            email='expenseupdate@example.com',
            password='testpass123',
            first_name='Expense',
            last_name='Updater'
        )
    
    def setUp(self):
        """Set up client and create expense for each test."""
        self.client = Client()
        self.client.login(email='expenseupdate@example.com', password='testpass123')
        
        self.expense = Expense.objects.create(
            item='Original Expense',
            cost=Decimal('10000.00'),
            expense_date=date(2026, 1, 15),
            notes='Original notes',
            created_by=self.user,
            modified_by=self.user
        )
    
    def test_success_message_on_expense_update(self):
        """Test that success message is shown after updating an expense."""
        response = self.client.post(
            reverse('expenses:update', kwargs={'pk': self.expense.pk}),
            {
                'item': 'Updated Expense',
                'cost': '15000',
                'expense_date': '20/01/2026'
            },
            follow=True
        )
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Expense 'Updated Expense' updated successfully.")
        self.assertEqual(messages[0].tags, 'success')
    
    def test_success_message_includes_item_name_on_update(self):
        """Test that update success message includes the item name."""
        response = self.client.post(
            reverse('expenses:update', kwargs={'pk': self.expense.pk}),
            {
                'item': 'New Item Name',
                'cost': '12000',
                'expense_date': '18/01/2026'
            },
            follow=True
        )
        
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('New Item Name', str(messages[0]))
        self.assertIn('updated successfully', str(messages[0]))
    
    def test_message_appears_on_list_page_after_update(self):
        """Test that message appears on list page after update."""
        response = self.client.post(
            reverse('expenses:update', kwargs={'pk': self.expense.pk}),
            {
                'item': 'List Page Expense',
                'cost': '8000',
                'expense_date': '22/01/2026'
            },
            follow=True
        )
        
        # Should redirect to list page
        self.assertTemplateUsed(response, 'expenses/expense_list.html')
        
        # Message should be in response
        self.assertContains(response, 'updated successfully')
    
    def test_no_message_on_update_validation_error(self):
        """Test that no success message on invalid update."""
        response = self.client.post(
            reverse('expenses:update', kwargs={'pk': self.expense.pk}),
            {
                'item': '',  # Empty item should fail
                'cost': '-100'  # Invalid cost
            }
        )
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)
    
    def test_success_message_after_updating_all_fields(self):
        """Test success message when updating all fields."""
        response = self.client.post(
            reverse('expenses:update', kwargs={'pk': self.expense.pk}),
            {
                'item': 'Fully Updated Expense',
                'cost': '50000.75',
                'expense_date': '25/01/2026',
                'notes': 'Updated notes with detailed description'
            },
            follow=True
        )
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('Fully Updated Expense', str(messages[0]))
        self.assertIn('updated successfully', str(messages[0]))


class ExpenseSuccessMessageEdgeCaseTests(TestCase):
    """Test edge cases for expense success messages."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test user."""
        cls.user = User.objects.create_user(
            email='expenseedge@example.com',
            password='testpass123',
            first_name='Expense',
            last_name='Edge'
        )
    
    def setUp(self):
        """Set up client."""
        self.client = Client()
        self.client.login(email='expenseedge@example.com', password='testpass123')
    
    def test_success_message_with_long_item_name(self):
        """Test success message with long item name."""
        long_item = 'A' * 100  # Long item name
        response = self.client.post(reverse('expenses:create'), {
            'item': long_item,
            'cost': '5000',
            'expense_date': '15/01/2026'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn(long_item, str(messages[0]))
    
    def test_success_message_with_large_amount(self):
        """Test success message with large cost."""
        response = self.client.post(reverse('expenses:create'), {
            'item': 'Large Expense',
            'cost': '9999999.99',
            'expense_date': '15/01/2026'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('Large Expense', str(messages[0]))
        self.assertIn('created successfully', str(messages[0]))
    
    def test_success_message_with_minimum_amount(self):
        """Test success message with minimum cost (0.01)."""
        response = self.client.post(reverse('expenses:create'), {
            'item': 'Tiny Expense',
            'cost': '0.01',
            'expense_date': '15/01/2026'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('Tiny Expense', str(messages[0]))
    
    def test_multiple_expense_creates_each_have_message(self):
        """Test that each expense create generates its own message."""
        # First create
        response1 = self.client.post(reverse('expenses:create'), {
            'item': 'First Expense',
            'cost': '1000',
            'expense_date': '15/01/2026'
        }, follow=True)
        messages1 = list(get_messages(response1.wsgi_request))
        self.assertEqual(len(messages1), 1)
        self.assertIn('First Expense', str(messages1[0]))
        
        # Second create
        response2 = self.client.post(reverse('expenses:create'), {
            'item': 'Second Expense',
            'cost': '2000',
            'expense_date': '16/01/2026'
        }, follow=True)
        messages2 = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages2), 1)
        self.assertIn('Second Expense', str(messages2[0]))
    
    def test_success_message_cleared_after_display(self):
        """Test that messages are cleared after being displayed."""
        # Create expense
        response = self.client.post(reverse('expenses:create'), {
            'item': 'Clearable Expense',
            'cost': '3000',
            'expense_date': '15/01/2026'
        }, follow=True)
        
        # First request should have message
        messages1 = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages1), 1)
        
        # Subsequent request should have no message
        response2 = self.client.get(reverse('expenses:list'))
        messages2 = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages2), 0)
    
    def test_success_message_with_very_old_date(self):
        """Test success message with historical expense date."""
        response = self.client.post(reverse('expenses:create'), {
            'item': 'Historical Expense',
            'cost': '15000',
            'expense_date': '01/01/2000'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('Historical Expense', str(messages[0]))
    
    def test_success_message_with_future_date(self):
        """Test success message with future expense date."""
        response = self.client.post(reverse('expenses:create'), {
            'item': 'Planned Expense',
            'cost': '50000',
            'expense_date': '01/01/2030'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('Planned Expense', str(messages[0]))
