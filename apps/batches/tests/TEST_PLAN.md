# Batch Module Unit Test Plan

## Overview
Comprehensive test coverage for the batches app including models, forms, views, and properties.

---

## 1. Batch Model Tests (`TestBatchModel`)

### Field Validation
- [ ] `batch_id` is unique and required
- [ ] `price` allows null/blank with default 0
- [ ] `tp_cost` allows null/blank
- [ ] `supply_date` allows null/blank
- [ ] `source` allows blank
- [ ] Bottle fields default to 0

### Properties
- [ ] `group_number` extracts last 3 chars correctly (e.g., "A24G02" → "G02")
- [ ] `group_number` handles short batch_id gracefully
- [ ] `total_bottles` sums all bottle fields correctly
- [ ] `total_cost` = price + tp_cost
- [ ] `total_cost` handles None values for price and tp_cost

### String Representation
- [ ] `__str__` returns batch_id

---

## 2. BatchForm Tests (`TestBatchForm`)

### Required Fields
- [ ] Only `batch_id` is required
- [ ] Form valid with only batch_id provided
- [ ] Form invalid without batch_id

### Optional Fields
- [ ] Form valid with empty price
- [ ] Form valid with empty tp_cost
- [ ] Form valid with empty bottle fields
- [ ] Form valid with empty source
- [ ] Form valid with empty notes

### Clean Methods
- [ ] Empty bottles_25cl converts to 0
- [ ] Empty bottles_75cl converts to 0
- [ ] Empty bottles_1L converts to 0
- [ ] Empty bottles_4L converts to 0
- [ ] Empty price converts to 0
- [ ] Empty tp_cost converts to None

### Date Parsing
- [ ] `clean_supply_date` parses dd/mm/yyyy format
- [ ] `clean_supply_date` parses YYYY-MM-DD fallback
- [ ] `clean_supply_date` returns None for empty input
- [ ] `clean_supply_date` raises error for invalid format

---

## 3. BatchListView Tests (`TestBatchListView`)

### GET Request
- [ ] Returns 200 for authenticated user
- [ ] Redirects unauthenticated user to login
- [ ] Uses correct template
- [ ] Batches ordered by created_at descending (newest first)

### Filtering
- [ ] Search by batch_id works
- [ ] Filter by group works
- [ ] Empty results handled correctly

### Pagination
- [ ] Paginate by 25 items

---

## 4. BatchCreateView Tests (`TestBatchCreateView`)

### GET Request
- [ ] Returns 200 for authenticated user
- [ ] Uses correct template
- [ ] Form in context

### POST Request
- [ ] Valid data creates batch
- [ ] Batch linked to user (created_by/modified_by)
- [ ] Redirects to list on success
- [ ] Invalid data returns form with errors
- [ ] Minimal data (only batch_id) creates batch successfully

---

## 5. BatchDetailView Tests (`TestBatchDetailView`)

### GET Request
- [ ] Returns 200 for valid batch
- [ ] Returns 404 for invalid ID
- [ ] Batch in context
- [ ] Uses correct template

---

## 6. BatchUpdateView Tests (`TestBatchUpdateView`)

### GET Request
- [ ] Returns 200 with pre-populated form
- [ ] Returns 404 for invalid ID

### POST Request
- [ ] Valid data updates batch
- [ ] Redirects to detail on success

---

## 7. BatchDeleteView Tests (`TestBatchDeleteView`)

### GET Request
- [ ] Returns confirmation page

### POST Request
- [ ] Deletes batch
- [ ] Redirects to list

---

## 8. Edge Cases & Boundary Conditions

### Batch ID Validation
- [ ] Duplicate batch_id rejected (unique constraint)
- [ ] Empty batch_id rejected
- [ ] Very long batch_id (50 chars max)
- [ ] batch_id with special characters
- [ ] batch_id with unicode characters
- [ ] batch_id with only numbers
- [ ] batch_id with spaces

### Numeric Fields
- [ ] Batch with all zeros for bottles
- [ ] Batch with very large price values (max_digits=10)
- [ ] Batch with decimal prices (2 decimal places)
- [ ] Negative price values (should they be allowed?)
- [ ] Negative bottle counts (should fail - PositiveIntegerField)
- [ ] Very large bottle counts
- [ ] Price at boundary (9999999999.99)

### Date Edge Cases
- [ ] Supply date in the future
- [ ] Supply date very far in past (e.g., year 1900)
- [ ] Invalid date format (mm/dd/yyyy vs dd/mm/yyyy)
- [ ] Date with invalid day (e.g., 31/02/2024)
- [ ] Date with invalid month (e.g., 13/01/2024)
- [ ] Leap year date (29/02/2024)

### Source Field
- [ ] Source with special characters (!@#$%^&*)
- [ ] Source with very long text (200 chars max)
- [ ] Source with HTML tags (XSS prevention)
- [ ] Source with newlines
- [ ] Source with emojis

### Notes Field
- [ ] Notes with very long text
- [ ] Notes with HTML tags
- [ ] Notes with markdown
- [ ] Empty notes

### Group Number Extraction
- [ ] batch_id shorter than 3 chars
- [ ] batch_id exactly 3 chars
- [ ] batch_id with non-standard format
- [ ] batch_id ending with numbers only

### Concurrent Operations
- [ ] Two users updating same batch simultaneously
- [ ] Creating batch while another with same ID is being created

### View Edge Cases
- [ ] Access batch detail with string ID (should 404)
- [ ] Access batch detail with negative ID
- [ ] Access non-existent batch
- [ ] Filter with SQL injection attempt
- [ ] Search with very long query string
- [ ] Pagination beyond available pages

### Form Submission Edge Cases
- [ ] Submit form with missing CSRF token
- [ ] Submit form with tampered data
- [ ] Submit same form twice (double submission)
- [ ] Submit with browser back button after success

---

## Test Count Summary

| Category | Tests |
|----------|-------|
| Model | 12 |
| Form | 14 |
| ListView | 6 |
| CreateView | 6 |
| DetailView | 4 |
| UpdateView | 4 |
| DeleteView | 3 |
| Edge Cases | 45 |
| **Total** | **94** |
