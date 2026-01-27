"""
Unit Tests for Sales Success Messages

This module provides comprehensive test coverage for success messages
displayed after sale create/update operations.

Test Categories:
1. Sale create success messages
2. Sale update success messages
3. Edge cases (special characters, concurrent operations)
"""

from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from apps.sales.models import Sale
from apps.batches.models import Batch
from apps.customers.models import Customer

User = get_user_model()


# =============================================================================
# SALE SUCCESS MESSAGE TESTS
# =============================================================================

class SaleCreateSuccessMessageTests(TestCase):
    """Test success messages for sale creation."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test user and required related objects."""
        cls.user = User.objects.create_user(
            email='salecreate@example.com',
            password='testpass123',
            first_name='Sale',
            last_name='Creator'
        )
        
        cls.batch = Batch.objects.create(
            batch_id='TESTBATCH001',
            supply_date='2026-01-01',
            price=Decimal('10000.00'),
            bottles_25cl=100,
            bottles_75cl=50,
            bottles_1L=30,
            bottles_4L=10,
            created_by=cls.user,
            modified_by=cls.user
        )
        
        cls.customer = Customer.objects.create(
            name='Test Customer',
            created_by=cls.user,
            modified_by=cls.user
        )
    
    def setUp(self):
        """Set up client."""
        self.client = Client()
        self.client.login(email='salecreate@example.com', password='testpass123')
    
    def test_success_message_on_sale_create(self):
        """Test that success message is shown after creating a sale."""
        response = self.client.post(reverse('sales:create'), {
            'customer': self.customer.pk,
            'customer_name': 'Test Customer',
            'bottle_type': '75CL',
            'unit_price': '5000',
            'quantity': '2',
            'batch': self.batch.pk,
            'payment_status': 'UNPAID'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('created successfully', str(messages[0]))
        self.assertEqual(messages[0].tags, 'success')
    
    def test_success_message_includes_sale_id(self):
        """Test that success message includes the sale ID (pk)."""
        response = self.client.post(reverse('sales:create'), {
            'customer': self.customer.pk,
            'customer_name': 'New Customer',
            'bottle_type': '1L',
            'unit_price': '8000',
            'quantity': '5',
            'batch': self.batch.pk,
            'payment_status': 'UNPAID'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        # Message format: "Sale #<pk> created successfully."
        self.assertIn('Sale #', str(messages[0]))
        self.assertIn('created successfully', str(messages[0]))
    
    def test_no_message_on_invalid_form(self):
        """Test that no success message is shown on form validation error."""
        response = self.client.post(reverse('sales:create'), {
            # Missing required fields
            'quantity': '10'
        })
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)
    
    def test_message_appears_on_list_page_after_redirect(self):
        """Test that message appears on list page after successful create."""
        response = self.client.post(reverse('sales:create'), {
            'customer': self.customer.pk,
            'customer_name': 'Redirect Customer',
            'bottle_type': '25CL',
            'unit_price': '2000',
            'quantity': '10',
            'batch': self.batch.pk,
            'payment_status': 'UNPAID'
        }, follow=True)
        
        # Should redirect to list page
        self.assertTemplateUsed(response, 'sales/sale_list.html')
        
        # Message should be in response
        self.assertContains(response, 'created successfully')


class SaleUpdateSuccessMessageTests(TestCase):
    """Test success messages for sale updates."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test user and required objects."""
        cls.user = User.objects.create_user(
            email='saleupdate@example.com',
            password='testpass123',
            first_name='Sale',
            last_name='Updater'
        )
        
        cls.batch = Batch.objects.create(
            batch_id='UPDATEBATCH001',
            supply_date='2026-01-01',
            price=Decimal('10000.00'),
            bottles_25cl=100,
            bottles_75cl=50,
            bottles_1L=30,
            bottles_4L=10,
            created_by=cls.user,
            modified_by=cls.user
        )
        
        cls.customer = Customer.objects.create(
            name='Update Customer',
            created_by=cls.user,
            modified_by=cls.user
        )
    
    def setUp(self):
        """Set up client and create sale for each test."""
        self.client = Client()
        self.client.login(email='saleupdate@example.com', password='testpass123')
        
        self.sale = Sale.objects.create(
            customer=self.customer,
            customer_name='Update Customer',
            bottle_type='75CL',
            unit_price=Decimal('5000.00'),
            quantity=2,
            total_price=Decimal('10000.00'),
            batch=self.batch,
            payment_status='UNPAID',
            created_by=self.user,
            modified_by=self.user
        )
    
    def test_success_message_on_sale_update(self):
        """Test that success message is shown after updating a sale."""
        response = self.client.post(
            reverse('sales:update', kwargs={'pk': self.sale.pk}),
            {
                'customer': self.customer.pk,
                'customer_name': 'Updated Customer Name',
                'bottle_type': '75CL',
                'unit_price': '6000',
                'quantity': '2',
                'batch': self.batch.pk,
                'payment_status': 'UNPAID'
            },
            follow=True
        )
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('updated successfully', str(messages[0]))
        self.assertEqual(messages[0].tags, 'success')
    
    def test_success_message_includes_sale_id_on_update(self):
        """Test that update success message includes the sale ID."""
        response = self.client.post(
            reverse('sales:update', kwargs={'pk': self.sale.pk}),
            {
                'customer': self.customer.pk,
                'customer_name': 'Updated Customer',
                'bottle_type': '1L',
                'unit_price': '8000',
                'quantity': '3',
                'batch': self.batch.pk,
                'payment_status': 'PARTIAL'
            },
            follow=True
        )
        
        messages = list(get_messages(response.wsgi_request))
        self.assertIn(f'Sale #{self.sale.pk}', str(messages[0]))
        self.assertIn('updated successfully', str(messages[0]))
    
    def test_message_appears_on_detail_page_after_update(self):
        """Test that message appears on detail page after update."""
        response = self.client.post(
            reverse('sales:update', kwargs={'pk': self.sale.pk}),
            {
                'customer': self.customer.pk,
                'customer_name': 'Detail Customer',
                'bottle_type': '75CL',
                'unit_price': '5500',
                'quantity': '2',
                'batch': self.batch.pk,
                'payment_status': 'UNPAID'
            },
            follow=True
        )
        
        # Should redirect to detail page
        self.assertTemplateUsed(response, 'sales/sale_detail.html')
        
        # Message should be in response
        self.assertContains(response, 'updated successfully')
    
    def test_no_message_on_update_validation_error(self):
        """Test that no success message on invalid update."""
        response = self.client.post(
            reverse('sales:update', kwargs={'pk': self.sale.pk}),
            {
                'customer_name': '',  # Empty should fail
                'quantity': '-1'  # Invalid
            }
        )
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)


class SaleSuccessMessageEdgeCaseTests(TestCase):
    """Test edge cases for sale success messages."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test user and required objects."""
        cls.user = User.objects.create_user(
            email='saleedge@example.com',
            password='testpass123',
            first_name='Sale',
            last_name='Edge'
        )
        
        cls.batch = Batch.objects.create(
            batch_id='EDGEBATCH001',
            supply_date='2026-01-01',
            price=Decimal('10000.00'),
            bottles_25cl=100,
            bottles_75cl=50,
            bottles_1L=30,
            bottles_4L=10,
            created_by=cls.user,
            modified_by=cls.user
        )
        
        cls.customer = Customer.objects.create(
            name='Edge Customer',
            created_by=cls.user,
            modified_by=cls.user
        )
    
    def setUp(self):
        """Set up client."""
        self.client = Client()
        self.client.login(email='saleedge@example.com', password='testpass123')
    
    def test_success_message_with_special_characters_in_customer_name(self):
        """Test success message with special characters in customer name."""
        response = self.client.post(reverse('sales:create'), {
            'customer': self.customer.pk,
            'customer_name': "John O'Brien & Co. <Ltd>",
            'bottle_type': '75CL',
            'unit_price': '5000',
            'quantity': '2',
            'batch': self.batch.pk,
            'payment_status': 'UNPAID'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('created successfully', str(messages[0]))
    
    def test_success_message_with_large_quantity(self):
        """Test success message with large quantity sale."""
        response = self.client.post(reverse('sales:create'), {
            'customer': self.customer.pk,
            'customer_name': 'Bulk Buyer',
            'bottle_type': '4L',
            'unit_price': '20000',
            'quantity': '999',
            'batch': self.batch.pk,
            'payment_status': 'UNPAID'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('created successfully', str(messages[0]))
    
    def test_success_message_with_paid_status(self):
        """Test success message when creating sale with PAID status."""
        response = self.client.post(reverse('sales:create'), {
            'customer': self.customer.pk,
            'customer_name': 'Paid Customer',
            'bottle_type': '25CL',
            'unit_price': '2000',
            'quantity': '5',
            'batch': self.batch.pk,
            'payment_status': 'PAID'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('created successfully', str(messages[0]))
    
    def test_multiple_sale_creates_each_have_message(self):
        """Test that each sale create generates its own message."""
        # First create
        response1 = self.client.post(reverse('sales:create'), {
            'customer': self.customer.pk,
            'customer_name': 'First Customer',
            'bottle_type': '75CL',
            'unit_price': '5000',
            'quantity': '1',
            'batch': self.batch.pk,
            'payment_status': 'UNPAID'
        }, follow=True)
        messages1 = list(get_messages(response1.wsgi_request))
        self.assertEqual(len(messages1), 1)
        
        # Second create
        response2 = self.client.post(reverse('sales:create'), {
            'customer': self.customer.pk,
            'customer_name': 'Second Customer',
            'bottle_type': '1L',
            'unit_price': '8000',
            'quantity': '2',
            'batch': self.batch.pk,
            'payment_status': 'UNPAID'
        }, follow=True)
        messages2 = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages2), 1)
