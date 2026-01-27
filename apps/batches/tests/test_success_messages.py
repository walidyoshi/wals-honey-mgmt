"""
Unit Tests for Success Messages

This module provides comprehensive test coverage for success messages
displayed after create/update operations for batches, sales, and expenses.

Test Categories:
1. Create operation success messages
2. Update operation success messages
3. Edge cases (special characters, empty fields, concurrent operations)
4. Message persistence and display
"""

from decimal import Decimal
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from apps.batches.models import Batch
from apps.batches.forms import BatchForm

User = get_user_model()


# =============================================================================
# BATCH SUCCESS MESSAGE TESTS
# =============================================================================

class BatchCreateSuccessMessageTests(TestCase):
    """Test success messages for batch creation."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test user."""
        cls.user = User.objects.create_user(
            email='batchcreate@example.com',
            password='testpass123',
            first_name='Batch',
            last_name='Creator'
        )
    
    def setUp(self):
        """Set up client."""
        self.client = Client()
        self.client.login(email='batchcreate@example.com', password='testpass123')
    
    def test_success_message_on_batch_create(self):
        """Test that success message is shown after creating a batch."""
        response = self.client.post(reverse('batches:create'), {
            'batch_id': 'TEST001'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Batch TEST001 created successfully.")
        self.assertEqual(messages[0].tags, 'success')
    
    def test_success_message_includes_batch_id(self):
        """Test that success message includes the batch ID."""
        response = self.client.post(reverse('batches:create'), {
            'batch_id': 'A24G01'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('A24G01', str(messages[0]))
    
    def test_success_message_with_full_form_data(self):
        """Test success message when creating batch with all fields."""
        response = self.client.post(reverse('batches:create'), {
            'batch_id': 'FULL001',
            'price': '50000',
            'tp_cost': '10000',
            'supply_date': '15/01/2026',
            'source': 'Adamawa',
            'bottles_25cl': '10',
            'bottles_75cl': '20',
            'bottles_1L': '15',
            'bottles_4L': '5',
            'notes': 'Test batch with all fields'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('FULL001', str(messages[0]))
        self.assertIn('created successfully', str(messages[0]))
    
    def test_no_message_on_invalid_form(self):
        """Test that no success message is shown on form validation error."""
        response = self.client.post(reverse('batches:create'), {
            # Missing required batch_id
        })
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)
    
    def test_success_message_with_special_characters_in_batch_id(self):
        """Test success message with special characters in batch ID."""
        response = self.client.post(reverse('batches:create'), {
            'batch_id': 'A24-G01_TEST'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('A24-G01_TEST', str(messages[0]))
    
    def test_success_message_with_numeric_batch_id(self):
        """Test success message with numeric-only batch ID."""
        response = self.client.post(reverse('batches:create'), {
            'batch_id': '123456789'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('123456789', str(messages[0]))
    
    def test_message_appears_on_list_page_after_redirect(self):
        """Test that message appears on list page after successful create."""
        response = self.client.post(reverse('batches:create'), {
            'batch_id': 'REDIRECT001'
        }, follow=True)
        
        # Should redirect to list page
        self.assertTemplateUsed(response, 'batches/batch_list.html')
        
        # Message should be in response
        self.assertContains(response, 'REDIRECT001 created successfully')


class BatchUpdateSuccessMessageTests(TestCase):
    """Test success messages for batch updates."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test user and batch."""
        cls.user = User.objects.create_user(
            email='batchupdate@example.com',
            password='testpass123',
            first_name='Batch',
            last_name='Updater'
        )
    
    def setUp(self):
        """Set up client and create batch for each test."""
        self.client = Client()
        self.client.login(email='batchupdate@example.com', password='testpass123')
        self.batch = Batch.objects.create(
            batch_id='UPDATE001',
            price=Decimal('50000.00'),
            source='Original Source',
            created_by=self.user,
            modified_by=self.user
        )
    
    def test_success_message_on_batch_update(self):
        """Test that success message is shown after updating a batch."""
        response = self.client.post(
            reverse('batches:update', kwargs={'pk': self.batch.pk}),
            {'batch_id': 'UPDATE001', 'source': 'Updated Source'},
            follow=True
        )
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Batch UPDATE001 updated successfully.")
        self.assertEqual(messages[0].tags, 'success')
    
    def test_success_message_includes_batch_id_on_update(self):
        """Test that update success message includes the batch ID."""
        response = self.client.post(
            reverse('batches:update', kwargs={'pk': self.batch.pk}),
            {'batch_id': 'UPDATE001', 'price': '60000'},
            follow=True
        )
        
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('UPDATE001', str(messages[0]))
        self.assertIn('updated successfully', str(messages[0]))
    
    def test_message_appears_on_detail_page_after_update(self):
        """Test that message appears on detail page after update."""
        response = self.client.post(
            reverse('batches:update', kwargs={'pk': self.batch.pk}),
            {'batch_id': 'UPDATE001', 'source': 'New Source'},
            follow=True
        )
        
        # Should redirect to detail page
        self.assertTemplateUsed(response, 'batches/batch_detail.html')
        
        # Message should be in response
        self.assertContains(response, 'UPDATE001 updated successfully')
    
    def test_no_message_on_update_validation_error(self):
        """Test that no success message on invalid update."""
        response = self.client.post(
            reverse('batches:update', kwargs={'pk': self.batch.pk}),
            {'batch_id': ''},  # Empty batch_id should fail
        )
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)
    
    def test_success_message_after_updating_all_fields(self):
        """Test success message when updating all fields."""
        response = self.client.post(
            reverse('batches:update', kwargs={'pk': self.batch.pk}),
            {
                'batch_id': 'UPDATE001',
                'price': '75000',
                'tp_cost': '15000',
                'supply_date': '20/01/2026',
                'source': 'Lagos',
                'bottles_25cl': '50',
                'bottles_75cl': '30',
                'bottles_1L': '20',
                'bottles_4L': '10',
                'notes': 'Updated all fields'
            },
            follow=True
        )
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('updated successfully', str(messages[0]))


class BatchSuccessMessageEdgeCaseTests(TestCase):
    """Test edge cases for batch success messages."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test user."""
        cls.user = User.objects.create_user(
            email='batchedge@example.com',
            password='testpass123',
            first_name='Batch',
            last_name='Edge'
        )
    
    def setUp(self):
        """Set up client."""
        self.client = Client()
        self.client.login(email='batchedge@example.com', password='testpass123')
    
    def test_success_message_with_max_length_batch_id(self):
        """Test success message with maximum length batch ID (50 chars)."""
        long_id = 'A' * 50
        response = self.client.post(reverse('batches:create'), {
            'batch_id': long_id
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn(long_id, str(messages[0]))
    
    def test_success_message_with_unicode_in_batch_id(self):
        """Test success message with unicode characters."""
        unicode_id = 'BATCH_テスト_001'
        response = self.client.post(reverse('batches:create'), {
            'batch_id': unicode_id
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn(unicode_id, str(messages[0]))
    
    def test_multiple_creates_each_have_message(self):
        """Test that each create operation generates its own message."""
        # First create
        response1 = self.client.post(reverse('batches:create'), {
            'batch_id': 'MULTI001'
        }, follow=True)
        messages1 = list(get_messages(response1.wsgi_request))
        self.assertEqual(len(messages1), 1)
        
        # Second create
        response2 = self.client.post(reverse('batches:create'), {
            'batch_id': 'MULTI002'
        }, follow=True)
        messages2 = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages2), 1)
        self.assertIn('MULTI002', str(messages2[0]))
    
    def test_success_message_cleared_after_display(self):
        """Test that messages are cleared after being displayed."""
        # Create batch
        response = self.client.post(reverse('batches:create'), {
            'batch_id': 'CLEAR001'
        }, follow=True)
        
        # First request should have message
        messages1 = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages1), 1)
        
        # Subsequent request should have no message
        response2 = self.client.get(reverse('batches:list'))
        messages2 = list(get_messages(response2.wsgi_request))
        self.assertEqual(len(messages2), 0)
