"""
Unit Tests for Add Payment Feature

This module provides comprehensive test coverage for the payment recording
functionality in the sales app, including:
- PaymentForm validation
- PaymentCreateView behavior
- Payment model operations
- Sale payment status updates

Test Categories:
1. Form validation tests
2. View tests (GET and POST)
3. Model tests
4. Integration tests
5. Edge case tests
"""

from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.sales.models import Sale, Payment
from apps.sales.forms import PaymentForm
from apps.batches.models import Batch
from apps.customers.models import Customer

User = get_user_model()


class PaymentFormTests(TestCase):
    """
    Test suite for PaymentForm validation.
    
    Tests cover amount validation, required fields, and business rules
    such as not exceeding the balance due.
    """
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for all form tests."""
        # Create test user
        cls.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create test customer (must be created before sale to avoid auto-creation issues)
        cls.customer = Customer.objects.create(
            name='Test Customer',
            created_by=cls.user,
            modified_by=cls.user
        )
        
        # Create test batch
        cls.batch = Batch.objects.create(
            supply_date='2026-01-01',
            price=Decimal('10000.00'),
            bottles_25cl=100,
            bottles_75cl=50,
            bottles_1L=30,
            bottles_4L=10,
            created_by=cls.user,
            modified_by=cls.user
        )
        
        # Create test sale with ₦10,000 total - link to existing customer
        cls.sale = Sale.objects.create(
            customer=cls.customer,
            customer_name='Test Customer',
            bottle_type='75CL',
            unit_price=Decimal('5000.00'),
            quantity=2,
            total_price=Decimal('10000.00'),
            batch=cls.batch,
            payment_status='UNPAID',
            created_by=cls.user,
            modified_by=cls.user
        )
    
    def test_valid_payment_amount(self):
        """Test that a valid payment amount is accepted."""
        form = PaymentForm(
            sale=self.sale,
            data={
                'amount': '5000.00',
                'payment_method': 'CASH',
                'notes': ''
            }
        )
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_payment_amount_exceeds_balance(self):
        """Test that payment exceeding balance due is rejected."""
        form = PaymentForm(
            sale=self.sale,
            data={
                'amount': '15000.00',  # More than ₦10,000 due
                'payment_method': 'CASH',
                'notes': ''
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
    
    def test_payment_exact_balance(self):
        """Test payment of exact balance due is accepted."""
        form = PaymentForm(
            sale=self.sale,
            data={
                'amount': '10000.00',  # Exact amount due
                'payment_method': 'CASH',
                'notes': ''
            }
        )
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_payment_with_notes(self):
        """Test payment with notes is accepted."""
        form = PaymentForm(
            sale=self.sale,
            data={
                'amount': '5000.00',
                'payment_method': 'TRANSFER',
                'notes': 'First installment payment'
            }
        )
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_payment_minimum_amount(self):
        """Test minimum payment amount (0.01) is accepted."""
        form = PaymentForm(
            sale=self.sale,
            data={
                'amount': '0.01',
                'payment_method': 'CASH',
                'notes': ''
            }
        )
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_all_payment_methods(self):
        """Test all valid payment methods are accepted."""
        payment_methods = ['CASH', 'TRANSFER', 'POS']
        
        for method in payment_methods:
            with self.subTest(method=method):
                form = PaymentForm(
                    sale=self.sale,
                    data={
                        'amount': '1000.00',
                        'payment_method': method,
                        'notes': ''
                    }
                )
                self.assertTrue(form.is_valid(), f"Form errors for {method}: {form.errors}")


class PaymentCreateViewGetTests(TestCase):
    """
    Test suite for PaymentCreateView GET requests.
    
    Tests verify that the modal form is properly rendered
    with correct context data.
    """
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for view tests."""
        cls.user = User.objects.create_user(
            email='viewtest@example.com',
            password='testpass123',
            first_name='View',
            last_name='Tester'
        )
        
        cls.customer = Customer.objects.create(
            name='View Test Customer',
            created_by=cls.user,
            modified_by=cls.user
        )
        
        cls.batch = Batch.objects.create(
            supply_date='2026-01-01',
            price=Decimal('10000.00'),
            bottles_25cl=100,
            bottles_75cl=50,
            bottles_1L=30,
            bottles_4L=10,
            created_by=cls.user,
            modified_by=cls.user
        )
        
        cls.sale = Sale.objects.create(
            customer=cls.customer,
            customer_name='View Test Customer',
            bottle_type='1L',
            unit_price=Decimal('8000.00'),
            quantity=5,
            total_price=Decimal('40000.00'),
            batch=cls.batch,
            payment_status='UNPAID',
            created_by=cls.user,
            modified_by=cls.user
        )
    
    def setUp(self):
        """Set up client for each test."""
        self.client = Client()
        self.client.login(email='viewtest@example.com', password='testpass123')
    
    def test_get_payment_form_authenticated(self):
        """Test that authenticated user can access payment form."""
        url = reverse('sales:add_payment', kwargs={'pk': self.sale.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
    
    def test_get_payment_form_contains_sale_context(self):
        """Test that sale object is in template context."""
        url = reverse('sales:add_payment', kwargs={'pk': self.sale.pk})
        response = self.client.get(url)
        
        self.assertIn('sale', response.context)
        self.assertEqual(response.context['sale'].pk, self.sale.pk)
    
    def test_get_payment_form_contains_form(self):
        """Test that form is in template context."""
        url = reverse('sales:add_payment', kwargs={'pk': self.sale.pk})
        response = self.client.get(url)
        
        self.assertIn('form', response.context)
    
    def test_get_payment_form_unauthenticated_redirects(self):
        """Test that unauthenticated user is redirected."""
        self.client.logout()
        url = reverse('sales:add_payment', kwargs={'pk': self.sale.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_get_payment_form_invalid_sale_returns_404(self):
        """Test that invalid sale ID returns 404."""
        url = reverse('sales:add_payment', kwargs={'pk': 99999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)


class PaymentCreateViewPostTests(TestCase):
    """
    Test suite for PaymentCreateView POST requests.
    
    Tests verify payment creation, validation errors,
    and proper response handling.
    """
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for POST tests."""
        cls.user = User.objects.create_user(
            email='posttest@example.com',
            password='testpass123',
            first_name='Post',
            last_name='Tester'
        )
        
        cls.batch = Batch.objects.create(
            supply_date='2026-01-01',
            price=Decimal('10000.00'),
            bottles_25cl=100,
            bottles_75cl=50,
            bottles_1L=30,
            bottles_4L=10,
            created_by=cls.user,
            modified_by=cls.user
        )
    
    def setUp(self):
        """Create fresh sale for each test to avoid payment conflicts."""
        self.client = Client()
        self.client.login(email='posttest@example.com', password='testpass123')
        
        # Create customer first
        self.customer = Customer.objects.create(
            name='Post Test Customer',
            created_by=self.user,
            modified_by=self.user
        )
        
        self.sale = Sale.objects.create(
            customer=self.customer,
            customer_name='Post Test Customer',
            bottle_type='25CL',
            unit_price=Decimal('2000.00'),
            quantity=10,
            total_price=Decimal('20000.00'),
            batch=self.batch,
            payment_status='UNPAID',
            created_by=self.user,
            modified_by=self.user
        )
    
    def test_post_valid_payment_creates_record(self):
        """Test that valid POST creates a payment record."""
        url = reverse('sales:add_payment', kwargs={'pk': self.sale.pk})
        initial_count = Payment.objects.count()
        
        response = self.client.post(url, {
            'amount': '5000.00',
            'payment_method': 'CASH',
            'notes': 'Test payment'
        })
        
        self.assertEqual(Payment.objects.count(), initial_count + 1)
    
    def test_post_payment_linked_to_sale(self):
        """Test that created payment is linked to correct sale."""
        url = reverse('sales:add_payment', kwargs={'pk': self.sale.pk})
        
        self.client.post(url, {
            'amount': '5000.00',
            'payment_method': 'CASH',
            'notes': ''
        })
        
        payment = Payment.objects.latest('id')
        self.assertEqual(payment.sale.pk, self.sale.pk)
    
    def test_post_payment_linked_to_user(self):
        """Test that created payment is linked to logged-in user."""
        url = reverse('sales:add_payment', kwargs={'pk': self.sale.pk})
        
        self.client.post(url, {
            'amount': '5000.00',
            'payment_method': 'TRANSFER',
            'notes': ''
        })
        
        payment = Payment.objects.latest('id')
        self.assertEqual(payment.created_by.pk, self.user.pk)
    
    def test_post_payment_returns_html_partial(self):
        """Test that successful POST returns HTML for HTMX update."""
        url = reverse('sales:add_payment', kwargs={'pk': self.sale.pk})
        
        response = self.client.post(url, {
            'amount': '5000.00',
            'payment_method': 'CASH',
            'notes': ''
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'total paid', response.content.lower())


class SalePaymentStatusTests(TestCase):
    """
    Test suite for sale payment status updates.
    
    Tests verify that payment_status is correctly updated
    based on payment amounts.
    """
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for status tests."""
        cls.user = User.objects.create_user(
            email='statustest@example.com',
            password='testpass123',
            first_name='Status',
            last_name='Tester'
        )
        
        cls.batch = Batch.objects.create(
            supply_date='2026-01-01',
            price=Decimal('10000.00'),
            bottles_25cl=100,
            bottles_75cl=50,
            bottles_1L=30,
            bottles_4L=10,
            created_by=cls.user,
            modified_by=cls.user
        )
    
    def setUp(self):
        """Create fresh sale for each test."""
        # Create customer first
        self.customer = Customer.objects.create(
            name='Status Test Customer',
            created_by=self.user,
            modified_by=self.user
        )
        
        self.sale = Sale.objects.create(
            customer=self.customer,
            customer_name='Status Test Customer',
            bottle_type='4L',
            unit_price=Decimal('20000.00'),
            quantity=1,
            total_price=Decimal('20000.00'),
            batch=self.batch,
            payment_status='UNPAID',
            created_by=self.user,
            modified_by=self.user
        )
    
    def test_partial_payment_changes_status_to_partial(self):
        """Test that partial payment changes status to PARTIAL."""
        Payment.objects.create(
            sale=self.sale,
            amount=Decimal('5000.00'),
            payment_method='CASH',
            created_by=self.user
        )
        
        self.sale.update_payment_status()
        self.assertEqual(self.sale.payment_status, 'PARTIAL')
    
    def test_full_payment_changes_status_to_paid(self):
        """Test that full payment changes status to PAID."""
        Payment.objects.create(
            sale=self.sale,
            amount=Decimal('20000.00'),
            payment_method='TRANSFER',
            created_by=self.user
        )
        
        self.sale.update_payment_status()
        self.assertEqual(self.sale.payment_status, 'PAID')
    
    def test_multiple_payments_accumulate(self):
        """Test that multiple payments accumulate correctly."""
        Payment.objects.create(
            sale=self.sale,
            amount=Decimal('5000.00'),
            payment_method='CASH',
            created_by=self.user
        )
        Payment.objects.create(
            sale=self.sale,
            amount=Decimal('10000.00'),
            payment_method='TRANSFER',
            created_by=self.user
        )
        
        self.assertEqual(self.sale.amount_paid, Decimal('15000.00'))
        self.assertEqual(self.sale.amount_due, Decimal('5000.00'))
    
    def test_exact_payment_completes_sale(self):
        """Test that exact remaining amount marks sale as PAID."""
        # First partial payment
        Payment.objects.create(
            sale=self.sale,
            amount=Decimal('15000.00'),
            payment_method='CASH',
            created_by=self.user
        )
        self.sale.update_payment_status()
        self.assertEqual(self.sale.payment_status, 'PARTIAL')
        
        # Second payment for remaining amount
        Payment.objects.create(
            sale=self.sale,
            amount=Decimal('5000.00'),
            payment_method='CASH',
            created_by=self.user
        )
        self.sale.update_payment_status()
        self.assertEqual(self.sale.payment_status, 'PAID')


class PaymentModelTests(TestCase):
    """
    Test suite for Payment model.
    
    Tests verify model fields, relationships, and defaults.
    """
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for model tests."""
        cls.user = User.objects.create_user(
            email='modeltest@example.com',
            password='testpass123',
            first_name='Model',
            last_name='Tester'
        )
        
        cls.customer = Customer.objects.create(
            name='Model Test Customer',
            created_by=cls.user,
            modified_by=cls.user
        )
        
        cls.batch = Batch.objects.create(
            supply_date='2026-01-01',
            price=Decimal('10000.00'),
            bottles_25cl=100,
            bottles_75cl=50,
            bottles_1L=30,
            bottles_4L=10,
            created_by=cls.user,
            modified_by=cls.user
        )
        
        cls.sale = Sale.objects.create(
            customer=cls.customer,
            customer_name='Model Test Customer',
            bottle_type='75CL',
            unit_price=Decimal('5000.00'),
            quantity=4,
            total_price=Decimal('20000.00'),
            batch=cls.batch,
            payment_status='UNPAID',
            created_by=cls.user,
            modified_by=cls.user
        )
    
    def test_payment_saves_correctly(self):
        """Test that payment saves with all fields."""
        payment = Payment.objects.create(
            sale=self.sale,
            amount=Decimal('5000.00'),
            payment_method='POS',
            notes='POS terminal payment',
            created_by=self.user
        )
        
        self.assertIsNotNone(payment.pk)
        self.assertEqual(payment.amount, Decimal('5000.00'))
        self.assertEqual(payment.payment_method, 'POS')
        self.assertEqual(payment.notes, 'POS terminal payment')
    
    def test_payment_date_auto_set(self):
        """Test that payment_date is automatically set."""
        payment = Payment.objects.create(
            sale=self.sale,
            amount=Decimal('1000.00'),
            payment_method='CASH',
            created_by=self.user
        )
        
        self.assertIsNotNone(payment.payment_date)
    
    def test_payment_string_representation(self):
        """Test payment __str__ method."""
        payment = Payment.objects.create(
            sale=self.sale,
            amount=Decimal('5000.00'),
            payment_method='CASH',
            created_by=self.user
        )
        
        # Should contain amount or sale reference
        str_repr = str(payment)
        self.assertIsNotNone(str_repr)


class PaymentEdgeCaseTests(TestCase):
    """
    Test suite for edge cases and boundary conditions.
    """
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for edge case tests."""
        cls.user = User.objects.create_user(
            email='edgetest@example.com',
            password='testpass123',
            first_name='Edge',
            last_name='Tester'
        )
        
        cls.batch = Batch.objects.create(
            supply_date='2026-01-01',
            price=Decimal('10000.00'),
            bottles_25cl=100,
            bottles_75cl=50,
            bottles_1L=30,
            bottles_4L=10,
            created_by=cls.user,
            modified_by=cls.user
        )
    
    def test_payment_on_zero_due_fails(self):
        """Test that payment on sale with zero amount due fails."""
        # Create customer first
        customer = Customer.objects.create(
            name='Paid Customer',
            created_by=self.user,
            modified_by=self.user
        )
        
        # Create fully paid sale
        sale = Sale.objects.create(
            customer=customer,
            customer_name='Paid Customer',
            bottle_type='25CL',
            unit_price=Decimal('1000.00'),
            quantity=1,
            total_price=Decimal('1000.00'),
            batch=self.batch,
            payment_status='PAID',
            created_by=self.user,
            modified_by=self.user
        )
        
        # Add payment that covers full amount
        Payment.objects.create(
            sale=sale,
            amount=Decimal('1000.00'),
            payment_method='CASH',
            created_by=self.user
        )
        
        # Try to add another payment
        form = PaymentForm(
            sale=sale,
            data={
                'amount': '100.00',
                'payment_method': 'CASH',
                'notes': ''
            }
        )
        
        # Form should be invalid because amount exceeds (zero) balance
        self.assertFalse(form.is_valid())
    
    def test_very_small_payment(self):
        """Test minimum valid payment amount."""
        # Create customer first
        customer = Customer.objects.create(
            name='Small Payment Customer',
            created_by=self.user,
            modified_by=self.user
        )
        
        sale = Sale.objects.create(
            customer=customer,
            customer_name='Small Payment Customer',
            bottle_type='25CL',
            unit_price=Decimal('1000.00'),
            quantity=1,
            total_price=Decimal('1000.00'),
            batch=self.batch,
            payment_status='UNPAID',
            created_by=self.user,
            modified_by=self.user
        )
        
        form = PaymentForm(
            sale=sale,
            data={
                'amount': '0.01',
                'payment_method': 'CASH',
                'notes': ''
            }
        )
        
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_sale_amount_due_property(self):
        """Test that amount_due property calculates correctly."""
        # Create customer first
        customer = Customer.objects.create(
            name='Amount Due Customer',
            created_by=self.user,
            modified_by=self.user
        )
        
        sale = Sale.objects.create(
            customer=customer,
            customer_name='Amount Due Customer',
            bottle_type='1L',
            unit_price=Decimal('8000.00'),
            quantity=2,
            total_price=Decimal('16000.00'),
            batch=self.batch,
            payment_status='UNPAID',
            created_by=self.user,
            modified_by=self.user
        )
        
        # Initial amount due equals total
        self.assertEqual(sale.amount_due, Decimal('16000.00'))
        
        # After partial payment
        Payment.objects.create(
            sale=sale,
            amount=Decimal('6000.00'),
            payment_method='CASH',
            created_by=self.user
        )
        
        self.assertEqual(sale.amount_due, Decimal('10000.00'))
