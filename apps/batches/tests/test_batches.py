"""
Unit Tests for Batch Module

Comprehensive test coverage for the batches app including:
- Batch model tests (fields, properties, validation)
- BatchForm tests (required fields, clean methods, date parsing)
- View tests (ListView, CreateView, DetailView, UpdateView, DeleteView)
- Edge cases and boundary conditions
"""

from decimal import Decimal
from datetime import date, datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.batches.models import Batch
from apps.batches.forms import BatchForm

User = get_user_model()


# =============================================================================
# MODEL TESTS
# =============================================================================

class BatchModelFieldTests(TestCase):
    """Test Batch model field validation and defaults."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test user for all model tests."""
        cls.user = User.objects.create_user(
            email='modeltest@example.com',
            password='testpass123',
            first_name='Model',
            last_name='Tester'
        )
    
    def test_batch_id_is_required(self):
        """Test that batch_id is required."""
        with self.assertRaises(IntegrityError):
            Batch.objects.create(
                batch_id=None,
                created_by=self.user,
                modified_by=self.user
            )
    
    def test_batch_id_is_unique(self):
        """Test that duplicate batch_id is rejected."""
        Batch.objects.create(
            batch_id='A24G01',
            created_by=self.user,
            modified_by=self.user
        )
        with self.assertRaises(IntegrityError):
            Batch.objects.create(
                batch_id='A24G01',
                created_by=self.user,
                modified_by=self.user
            )
    
    def test_price_allows_null_with_default(self):
        """Test that price allows null and defaults to 0."""
        batch = Batch.objects.create(
            batch_id='A24G02',
            created_by=self.user,
            modified_by=self.user
        )
        self.assertEqual(batch.price, 0)
    
    def test_tp_cost_allows_null(self):
        """Test that tp_cost allows null."""
        batch = Batch.objects.create(
            batch_id='A24G03',
            created_by=self.user,
            modified_by=self.user
        )
        self.assertIsNone(batch.tp_cost)
    
    def test_supply_date_allows_null(self):
        """Test that supply_date allows null."""
        batch = Batch.objects.create(
            batch_id='A24G04',
            created_by=self.user,
            modified_by=self.user
        )
        self.assertIsNone(batch.supply_date)
    
    def test_source_allows_blank(self):
        """Test that source allows blank."""
        batch = Batch.objects.create(
            batch_id='A24G05',
            source='',
            created_by=self.user,
            modified_by=self.user
        )
        self.assertEqual(batch.source, '')
    
    def test_bottle_fields_default_to_zero(self):
        """Test that all bottle fields default to 0."""
        batch = Batch.objects.create(
            batch_id='A24G06',
            created_by=self.user,
            modified_by=self.user
        )
        self.assertEqual(batch.bottles_25cl, 0)
        self.assertEqual(batch.bottles_75cl, 0)
        self.assertEqual(batch.bottles_1L, 0)
        self.assertEqual(batch.bottles_4L, 0)


class BatchModelPropertyTests(TestCase):
    """Test Batch model computed properties."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test user and batch for property tests."""
        cls.user = User.objects.create_user(
            email='proptest@example.com',
            password='testpass123',
            first_name='Property',
            last_name='Tester'
        )
    
    def test_group_number_extracts_last_3_chars(self):
        """Test group_number extracts last 3 characters."""
        batch = Batch.objects.create(
            batch_id='A24G02',
            created_by=self.user,
            modified_by=self.user
        )
        self.assertEqual(batch.group_number, 'G02')
    
    def test_group_number_with_short_batch_id(self):
        """Test group_number handles short batch_id."""
        batch = Batch.objects.create(
            batch_id='AB',
            created_by=self.user,
            modified_by=self.user
        )
        self.assertEqual(batch.group_number, '')
    
    def test_group_number_exactly_3_chars(self):
        """Test group_number with exactly 3 char batch_id."""
        batch = Batch.objects.create(
            batch_id='G01',
            created_by=self.user,
            modified_by=self.user
        )
        self.assertEqual(batch.group_number, 'G01')
    
    def test_total_bottles_sums_all_sizes(self):
        """Test total_bottles sums all bottle fields."""
        batch = Batch.objects.create(
            batch_id='A24G07',
            bottles_25cl=10,
            bottles_75cl=20,
            bottles_1L=30,
            bottles_4L=5,
            created_by=self.user,
            modified_by=self.user
        )
        self.assertEqual(batch.total_bottles, 65)
    
    def test_total_bottles_with_zeros(self):
        """Test total_bottles with all zeros."""
        batch = Batch.objects.create(
            batch_id='A24G08',
            created_by=self.user,
            modified_by=self.user
        )
        self.assertEqual(batch.total_bottles, 0)
    
    def test_total_cost_with_both_values(self):
        """Test total_cost = price + tp_cost."""
        batch = Batch.objects.create(
            batch_id='A24G09',
            price=Decimal('50000.00'),
            tp_cost=Decimal('10000.00'),
            created_by=self.user,
            modified_by=self.user
        )
        self.assertEqual(batch.total_cost, Decimal('60000.00'))
    
    def test_total_cost_with_none_tp_cost(self):
        """Test total_cost handles None tp_cost."""
        batch = Batch.objects.create(
            batch_id='A24G10',
            price=Decimal('50000.00'),
            tp_cost=None,
            created_by=self.user,
            modified_by=self.user
        )
        self.assertEqual(batch.total_cost, Decimal('50000.00'))
    
    def test_total_cost_with_none_price(self):
        """Test total_cost handles None price."""
        batch = Batch.objects.create(
            batch_id='A24G11',
            price=None,
            tp_cost=Decimal('5000.00'),
            created_by=self.user,
            modified_by=self.user
        )
        self.assertEqual(batch.total_cost, Decimal('5000.00'))
    
    def test_total_cost_with_both_none(self):
        """Test total_cost handles both None."""
        batch = Batch.objects.create(
            batch_id='A24G12',
            price=None,
            tp_cost=None,
            created_by=self.user,
            modified_by=self.user
        )
        self.assertEqual(batch.total_cost, 0)
    
    def test_str_returns_batch_id(self):
        """Test __str__ returns batch_id."""
        batch = Batch.objects.create(
            batch_id='A24G13',
            created_by=self.user,
            modified_by=self.user
        )
        self.assertEqual(str(batch), 'A24G13')


# =============================================================================
# FORM TESTS
# =============================================================================

class BatchFormRequiredFieldsTests(TestCase):
    """Test BatchForm required field validation."""
    
    def test_form_valid_with_only_batch_id(self):
        """Test form is valid with only batch_id."""
        form = BatchForm(data={'batch_id': 'A24G01'})
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_form_invalid_without_batch_id(self):
        """Test form is invalid without batch_id."""
        form = BatchForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('batch_id', form.errors)
    
    def test_form_valid_with_empty_price(self):
        """Test form is valid with empty price."""
        form = BatchForm(data={'batch_id': 'A24G02', 'price': ''})
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_form_valid_with_empty_tp_cost(self):
        """Test form is valid with empty tp_cost."""
        form = BatchForm(data={'batch_id': 'A24G03', 'tp_cost': ''})
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_form_valid_with_empty_bottle_fields(self):
        """Test form is valid with empty bottle fields."""
        form = BatchForm(data={
            'batch_id': 'A24G04',
            'bottles_25cl': '',
            'bottles_75cl': '',
            'bottles_1L': '',
            'bottles_4L': ''
        })
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_form_valid_with_all_fields(self):
        """Test form is valid with all fields populated."""
        form = BatchForm(data={
            'batch_id': 'A24G05',
            'price': '50000',
            'tp_cost': '10000',
            'supply_date': '15/01/2026',
            'source': 'Adamawa',
            'bottles_25cl': '10',
            'bottles_75cl': '20',
            'bottles_1L': '15',
            'bottles_4L': '5',
            'notes': 'Test batch'
        })
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")


class BatchFormCleanMethodsTests(TestCase):
    """Test BatchForm clean methods for empty value conversion."""
    
    def test_clean_bottles_25cl_converts_empty_to_zero(self):
        """Test empty bottles_25cl converts to 0."""
        form = BatchForm(data={'batch_id': 'A24G01', 'bottles_25cl': ''})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['bottles_25cl'], 0)
    
    def test_clean_bottles_75cl_converts_empty_to_zero(self):
        """Test empty bottles_75cl converts to 0."""
        form = BatchForm(data={'batch_id': 'A24G02', 'bottles_75cl': ''})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['bottles_75cl'], 0)
    
    def test_clean_bottles_1L_converts_empty_to_zero(self):
        """Test empty bottles_1L converts to 0."""
        form = BatchForm(data={'batch_id': 'A24G03', 'bottles_1L': ''})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['bottles_1L'], 0)
    
    def test_clean_bottles_4L_converts_empty_to_zero(self):
        """Test empty bottles_4L converts to 0."""
        form = BatchForm(data={'batch_id': 'A24G04', 'bottles_4L': ''})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['bottles_4L'], 0)
    
    def test_clean_price_converts_empty_to_zero(self):
        """Test empty price converts to 0."""
        form = BatchForm(data={'batch_id': 'A24G05', 'price': ''})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['price'], 0)
    
    def test_clean_tp_cost_converts_empty_to_none(self):
        """Test empty tp_cost converts to None."""
        form = BatchForm(data={'batch_id': 'A24G06', 'tp_cost': ''})
        self.assertTrue(form.is_valid())
        self.assertIsNone(form.cleaned_data['tp_cost'])


class BatchFormDateParsingTests(TestCase):
    """Test BatchForm supply_date parsing."""
    
    def test_parse_dd_mm_yyyy_format(self):
        """Test parsing dd/mm/yyyy format."""
        form = BatchForm(data={'batch_id': 'A24G01', 'supply_date': '15/01/2026'})
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertEqual(form.cleaned_data['supply_date'], date(2026, 1, 15))
    
    def test_parse_yyyy_mm_dd_fallback(self):
        """Test parsing YYYY-MM-DD fallback format."""
        form = BatchForm(data={'batch_id': 'A24G02', 'supply_date': '2026-01-15'})
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertEqual(form.cleaned_data['supply_date'], date(2026, 1, 15))
    
    def test_empty_supply_date_returns_none(self):
        """Test empty supply_date returns None."""
        form = BatchForm(data={'batch_id': 'A24G03', 'supply_date': ''})
        self.assertTrue(form.is_valid())
        self.assertIsNone(form.cleaned_data['supply_date'])
    
    def test_invalid_date_format_raises_error(self):
        """Test invalid date format raises error."""
        form = BatchForm(data={'batch_id': 'A24G04', 'supply_date': 'invalid'})
        self.assertFalse(form.is_valid())
        self.assertIn('supply_date', form.errors)
    
    def test_leap_year_date(self):
        """Test leap year date (29/02/2024) is valid."""
        form = BatchForm(data={'batch_id': 'A24G05', 'supply_date': '29/02/2024'})
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertEqual(form.cleaned_data['supply_date'], date(2024, 2, 29))
    
    def test_invalid_day_raises_error(self):
        """Test invalid day (31/02/2024) raises error."""
        form = BatchForm(data={'batch_id': 'A24G06', 'supply_date': '31/02/2024'})
        self.assertFalse(form.is_valid())
        self.assertIn('supply_date', form.errors)


# =============================================================================
# VIEW TESTS
# =============================================================================

class BatchListViewTests(TestCase):
    """Test BatchListView functionality."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test data for list view tests."""
        cls.user = User.objects.create_user(
            email='listtest@example.com',
            password='testpass123',
            first_name='List',
            last_name='Tester'
        )
        
        # Create multiple batches
        for i in range(5):
            Batch.objects.create(
                batch_id=f'A24G{i:02d}',
                price=Decimal('50000.00'),
                source='Test Source',
                created_by=cls.user,
                modified_by=cls.user
            )
    
    def setUp(self):
        """Set up client for tests."""
        self.client = Client()
        self.client.login(email='listtest@example.com', password='testpass123')
    
    def test_get_returns_200(self):
        """Test GET returns 200 for authenticated user."""
        response = self.client.get(reverse('batches:list'))
        self.assertEqual(response.status_code, 200)
    
    def test_unauthenticated_redirects_to_login(self):
        """Test unauthenticated user is redirected."""
        self.client.logout()
        response = self.client.get(reverse('batches:list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_uses_correct_template(self):
        """Test view uses correct template."""
        response = self.client.get(reverse('batches:list'))
        self.assertTemplateUsed(response, 'batches/batch_list.html')
    
    def test_batches_in_context(self):
        """Test batches are in context."""
        response = self.client.get(reverse('batches:list'))
        self.assertIn('batches', response.context)
    
    def test_batches_ordered_by_created_at_desc(self):
        """Test batches are ordered by created_at descending."""
        response = self.client.get(reverse('batches:list'))
        batches = list(response.context['batches'])
        # Check that each batch was created before the next
        for i in range(len(batches) - 1):
            self.assertGreaterEqual(batches[i].created_at, batches[i + 1].created_at)
    
    def test_search_filter_works(self):
        """Test search filter by batch_id."""
        response = self.client.get(reverse('batches:list'), {'search': 'G01'})
        batches = response.context['batches']
        for batch in batches:
            self.assertIn('G01', batch.batch_id)
    
    def test_group_filter_works(self):
        """Test group filter."""
        response = self.client.get(reverse('batches:list'), {'group': 'G02'})
        batches = response.context['batches']
        for batch in batches:
            self.assertTrue(batch.batch_id.endswith('G02'))


class BatchCreateViewTests(TestCase):
    """Test BatchCreateView functionality."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test user."""
        cls.user = User.objects.create_user(
            email='createtest@example.com',
            password='testpass123',
            first_name='Create',
            last_name='Tester'
        )
    
    def setUp(self):
        """Set up client."""
        self.client = Client()
        self.client.login(email='createtest@example.com', password='testpass123')
    
    def test_get_returns_200(self):
        """Test GET returns 200."""
        response = self.client.get(reverse('batches:create'))
        self.assertEqual(response.status_code, 200)
    
    def test_uses_correct_template(self):
        """Test uses correct template."""
        response = self.client.get(reverse('batches:create'))
        self.assertTemplateUsed(response, 'batches/batch_form.html')
    
    def test_form_in_context(self):
        """Test form is in context."""
        response = self.client.get(reverse('batches:create'))
        self.assertIn('form', response.context)
    
    def test_post_valid_data_creates_batch(self):
        """Test POST with valid data creates batch."""
        initial_count = Batch.objects.count()
        response = self.client.post(reverse('batches:create'), {
            'batch_id': 'A24G99',
            'price': '50000',
            'bottles_25cl': '10'
        })
        self.assertEqual(Batch.objects.count(), initial_count + 1)
    
    def test_post_minimal_data_creates_batch(self):
        """Test POST with only batch_id creates batch."""
        response = self.client.post(reverse('batches:create'), {
            'batch_id': 'A24G98'
        })
        self.assertTrue(Batch.objects.filter(batch_id='A24G98').exists())
    
    def test_post_redirects_on_success(self):
        """Test POST redirects to list on success."""
        response = self.client.post(reverse('batches:create'), {
            'batch_id': 'A24G97'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('batches:list'))
    
    def test_post_invalid_data_returns_form(self):
        """Test POST with invalid data returns form with errors."""
        response = self.client.post(reverse('batches:create'), {})
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)


class BatchDetailViewTests(TestCase):
    """Test BatchDetailView functionality."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test data."""
        cls.user = User.objects.create_user(
            email='detailtest@example.com',
            password='testpass123',
            first_name='Detail',
            last_name='Tester'
        )
        cls.batch = Batch.objects.create(
            batch_id='A24G01',
            price=Decimal('50000.00'),
            tp_cost=Decimal('10000.00'),
            bottles_25cl=10,
            created_by=cls.user,
            modified_by=cls.user
        )
    
    def setUp(self):
        """Set up client."""
        self.client = Client()
        self.client.login(email='detailtest@example.com', password='testpass123')
    
    def test_get_returns_200_for_valid_batch(self):
        """Test GET returns 200 for valid batch."""
        response = self.client.get(reverse('batches:detail', kwargs={'pk': self.batch.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_returns_404_for_invalid_id(self):
        """Test returns 404 for invalid ID."""
        response = self.client.get(reverse('batches:detail', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)
    
    def test_batch_in_context(self):
        """Test batch is in context."""
        response = self.client.get(reverse('batches:detail', kwargs={'pk': self.batch.pk}))
        self.assertIn('batch', response.context)
        self.assertEqual(response.context['batch'].pk, self.batch.pk)
    
    def test_uses_correct_template(self):
        """Test uses correct template."""
        response = self.client.get(reverse('batches:detail', kwargs={'pk': self.batch.pk}))
        self.assertTemplateUsed(response, 'batches/batch_detail.html')


class BatchUpdateViewTests(TestCase):
    """Test BatchUpdateView functionality."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test data."""
        cls.user = User.objects.create_user(
            email='updatetest@example.com',
            password='testpass123',
            first_name='Update',
            last_name='Tester'
        )
        cls.batch = Batch.objects.create(
            batch_id='A24G01',
            price=Decimal('50000.00'),
            source='Original Source',
            created_by=cls.user,
            modified_by=cls.user
        )
    
    def setUp(self):
        """Set up client."""
        self.client = Client()
        self.client.login(email='updatetest@example.com', password='testpass123')
    
    def test_get_returns_200(self):
        """Test GET returns 200."""
        response = self.client.get(reverse('batches:update', kwargs={'pk': self.batch.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_form_prepopulated(self):
        """Test form is pre-populated with batch data."""
        response = self.client.get(reverse('batches:update', kwargs={'pk': self.batch.pk}))
        form = response.context['form']
        self.assertEqual(form.initial.get('batch_id') or form.instance.batch_id, 'A24G01')
    
    def test_post_updates_batch(self):
        """Test POST updates batch."""
        response = self.client.post(reverse('batches:update', kwargs={'pk': self.batch.pk}), {
            'batch_id': 'A24G01',
            'source': 'Updated Source'
        })
        self.batch.refresh_from_db()
        self.assertEqual(self.batch.source, 'Updated Source')
    
    def test_post_redirects_to_detail(self):
        """Test POST redirects to detail page."""
        response = self.client.post(reverse('batches:update', kwargs={'pk': self.batch.pk}), {
            'batch_id': 'A24G01',
            'source': 'Test'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('batches:detail', kwargs={'pk': self.batch.pk}))


class BatchDeleteViewTests(TestCase):
    """Test BatchDeleteView functionality."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test user."""
        cls.user = User.objects.create_user(
            email='deletetest@example.com',
            password='testpass123',
            first_name='Delete',
            last_name='Tester'
        )
    
    def setUp(self):
        """Set up client and create batch for each test."""
        self.client = Client()
        self.client.login(email='deletetest@example.com', password='testpass123')
        self.batch = Batch.objects.create(
            batch_id='A24G01',
            created_by=self.user,
            modified_by=self.user
        )
    
    def test_get_returns_confirmation_page(self):
        """Test GET returns confirmation page."""
        response = self.client.get(reverse('batches:delete', kwargs={'pk': self.batch.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'batches/batch_confirm_delete.html')
    
    def test_post_deletes_batch(self):
        """Test POST deletes batch."""
        batch_id = self.batch.pk
        response = self.client.post(reverse('batches:delete', kwargs={'pk': batch_id}))
        self.assertFalse(Batch.objects.filter(pk=batch_id).exists())
    
    def test_post_redirects_to_list(self):
        """Test POST redirects to list."""
        response = self.client.post(reverse('batches:delete', kwargs={'pk': self.batch.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('batches:list'))


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class BatchEdgeCaseTests(TestCase):
    """Test edge cases and boundary conditions."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test user."""
        cls.user = User.objects.create_user(
            email='edgetest@example.com',
            password='testpass123',
            first_name='Edge',
            last_name='Tester'
        )
    
    def setUp(self):
        """Set up client."""
        self.client = Client()
        self.client.login(email='edgetest@example.com', password='testpass123')
    
    def test_batch_id_max_length(self):
        """Test batch_id at max length (50 chars)."""
        long_id = 'A' * 50
        batch = Batch.objects.create(
            batch_id=long_id,
            created_by=self.user,
            modified_by=self.user
        )
        self.assertEqual(len(batch.batch_id), 50)
    
    def test_batch_id_with_special_characters(self):
        """Test batch_id with special characters."""
        form = BatchForm(data={'batch_id': 'A24-G01_TEST'})
        self.assertTrue(form.is_valid())
    
    def test_batch_id_with_numbers_only(self):
        """Test batch_id with only numbers."""
        form = BatchForm(data={'batch_id': '123456789'})
        self.assertTrue(form.is_valid())
    
    def test_large_price_value(self):
        """Test very large price value."""
        batch = Batch.objects.create(
            batch_id='A24LARGE',
            price=Decimal('9999999.99'),
            created_by=self.user,
            modified_by=self.user
        )
        self.assertEqual(batch.price, Decimal('9999999.99'))
    
    def test_decimal_price_precision(self):
        """Test decimal price with 2 decimal places."""
        batch = Batch.objects.create(
            batch_id='A24DECIMAL',
            price=Decimal('12345.67'),
            created_by=self.user,
            modified_by=self.user
        )
        self.assertEqual(batch.price, Decimal('12345.67'))
    
    def test_source_with_special_characters(self):
        """Test source with special characters."""
        batch = Batch.objects.create(
            batch_id='A24SPECIAL',
            source='Test & Source <script>',
            created_by=self.user,
            modified_by=self.user
        )
        self.assertEqual(batch.source, 'Test & Source <script>')
    
    def test_source_max_length(self):
        """Test source at max length (200 chars)."""
        long_source = 'A' * 200
        batch = Batch.objects.create(
            batch_id='A24LONGSRC',
            source=long_source,
            created_by=self.user,
            modified_by=self.user
        )
        self.assertEqual(len(batch.source), 200)
    
    def test_access_nonexistent_batch_detail(self):
        """Test accessing non-existent batch returns 404."""
        response = self.client.get(reverse('batches:detail', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)
    
    def test_search_with_empty_string(self):
        """Test search with empty string returns all."""
        Batch.objects.create(
            batch_id='A24TEST',
            created_by=self.user,
            modified_by=self.user
        )
        response = self.client.get(reverse('batches:list'), {'search': ''})
        self.assertEqual(response.status_code, 200)
    
    def test_future_supply_date(self):
        """Test supply date in the future is allowed."""
        form = BatchForm(data={
            'batch_id': 'A24FUTURE',
            'supply_date': '01/01/2030'
        })
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_very_old_supply_date(self):
        """Test very old supply date is allowed."""
        form = BatchForm(data={
            'batch_id': 'A24OLD',
            'supply_date': '01/01/1990'
        })
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_notes_with_long_text(self):
        """Test notes with very long text."""
        long_notes = 'Test notes. ' * 1000
        batch = Batch.objects.create(
            batch_id='A24LONGNOTES',
            notes=long_notes,
            created_by=self.user,
            modified_by=self.user
        )
        self.assertEqual(batch.notes, long_notes)
