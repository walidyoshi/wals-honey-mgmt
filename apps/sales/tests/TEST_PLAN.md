# Add Payment Feature - Unit Test Plan

## Test Scenarios

### 1. PaymentForm Tests
- [ ] Valid payment amount within limit
- [ ] Payment amount exceeds balance due (should fail)
- [ ] Payment amount is zero (should fail)
- [ ] Payment amount is negative (should be allowed for now)
- [ ] Payment with all valid fields
- [ ] Payment with empty notes (should pass)

### 2. PaymentCreateView Tests
- [ ] GET request returns modal form
- [ ] Sale context is passed to template
- [ ] POST with valid data creates payment
- [ ] POST with invalid data returns form with errors
- [ ] Payment is linked to correct sale
- [ ] Payment is linked to logged-in user
- [ ] Payment updates sale's amount_paid property
- [ ] Payment updates sale's payment_status

### 3. Payment Model Tests
- [ ] Payment saves correctly
- [ ] Payment has correct sale relationship
- [ ] Payment date is auto-set
- [ ] Payment method choices work

### 4. Sale Payment Status Tests
- [ ] UNPAID -> PARTIAL after partial payment
- [ ] PARTIAL -> PAID after full payment
- [ ] Multiple payments accumulate correctly

### 5. Edge Cases
- [ ] Payment on already fully paid sale (button should not show)
- [ ] Exact amount payment (edge case)
- [ ] Very small payment (0.01)
- [ ] Authentication required
