# System Architecture

## Overview
The Wals Honey Management System is a modular Django application designed with **Separation of Concerns**, **DRY (Don't Repeat Yourself)** principles, and a **Mobile-First** approach. It is built to handle the specific workflow of honey acquisition, processing, and sales, with a strong emphasis on auditability and data integrity.

## Design Principles
1.  **Separation of Concerns**: Functionality is split into distinct apps (batches, sales, customers) to minimize coupling.
2.  **Audit Trail**: Critical models (Sales, Batches) have associated signals or audit logs to track changes (who, what, when).
3.  **Mobile-First UI**: The frontend uses responsive design and HTMX for partial page updates, ensuring usability on tablets and phones in the field.
4.  **Fat Models, Thin Views**: Business logic is encapsulated in models and methods rather than views, ensuring consistency.

## Module Architecture

```text
[ User ]
   │
   ▼
[ View / Template (HTMX) ]
   │
   ▼
[ Model (Business Logic) ] ───► [ Signal (Audit/Side Effects) ]
   │
   ▼
[ Database (PostgreSQL/SQLite) ]
```

### Application Breakdown

#### 1. Core (`apps/core/`)
**Purpose**: Provides base functionality and utilities shared across all other apps.
-   **Base Models**: `TimeStampedModel`, `UserTrackingModel` (for automatic `created_by` / `updated_by` fields).
-   **Middleware**: `UserTrackingMiddleware` captures the current user from the request for model usage.
-   **Template Tags**: Custom tags like `audit_tags` for formatting change logs.

#### 2. Accounts (`apps/accounts/`)
**Purpose**: Manages user authentication and authorization.
-   **User Model**: Custom user model extending `AbstractUser`.
-   **Role-Based Access**: Distinguishes between admins and regular staff (configurable via groups/permissions).

#### 3. Customers (`apps/customers/`)
**Purpose**: Stores basic customer information and purchase history.
-   **Models**: `Customer` stores  info and tracks aggregated sales data.
-   **Components**: Simple autocomplete search for linking sales to customers.

#### 4. Batches (`apps/batches/`)
**Purpose**: The core inventory tracking module.
-   **Models**: `Batch` represents a collection of honey (e.g., specific jerrycans from a supplier).
-   **Properties**: 
    -   `total_cost`: Calculated as price + transport cost.
    -   `total_bottles`: Sum of all bottle sizes (25cl, 75cl, 1L, 4L).
    -   `group_number`: Extracts group identifier from batch_id.
-   **Forms**: Flexible creation - only `batch_id` is required; all other fields optional.
-   **Views**: Responsive list (table on desktop, cards on mobile), ordered by newest entry first.
-   **Audit**: `AuditLog` tracks all modifications to batch records.
-   **Tests**: 72 unit tests covering models, forms, views, and edge cases.

#### 5. Sales (`apps/sales/`)
**Purpose**: Manages transactions and payments.
-   **Models**:
    -   `Sale`: The header record for a transaction (Customer, Date, Total Amount).
    -   `Payment`: Tracks partial or full payments against a sale.
-   **Features**:
    -   HTMX-powered payment modal with confirmation dialog.
    -   Automatic payment status updates (UNPAID → PARTIAL → PAID).
    -   Payment validation prevents overpayment.
-   **Signals**: Automatically updates `Sale` payment status when a `Payment` is recorded or deleted.
-   **Tests**: 25 unit tests for payment functionality.

#### 6. Expenses (`apps/expenses/`)
**Purpose**: Tracks operational costs unrelated to direct honey purchase (e.g., transport, packaging).
-   **Models**: `Expense` record with category, amount, and date.

## Configuration Structure
The project configuration is split to support multiple environments easily:
-   `config/settings/base.py`: Shared settings (Installed apps, middleware).
-   `config/settings/development.py`: Debug mode on, local SQLite db.
-   `config/settings/production.py`: Debug off, security headers, production DB config (e.g., Dj-Database-Url).

## Data Flow & Signals
The system relies heavily on **Django Signals** to maintain data integrity without cluttering views.
-   **Example**: When a `Payment` is saved:
    1.  `post_save` signal triggers.
    2.  The handler calculates the total payments for the related `Sale`.
    3.  It compares this to the `Sale.total_amount`.
    4.  It updates `Sale.status` (e.g., to 'PAID') automatically.

## Security Features
-   **CSRF Protection**: Standard Django CSRF tokens on all forms.
-   **Authentication**: Required for all data-modification views.
-   **Input Validation**: Strict validation on forms (numeric checks, date formats).

## Scalability
-   **Database**: Designed to run on PostgreSQL for production reliability.
-   **Static Files**: Served via WhiteNoise in production for efficiency.
-   **Modular Apps**: New features (e.g., "Processing" or "Packaging") can be added as new apps without rewriting core logic.
