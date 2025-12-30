# Wals Honey Management System

A comprehensive Django-based management system for honey bottling and distribution.

## Features

*   **Modular Architecture**: Separate apps for Accounts, Customers, Batches, Sales, and Expenses.
*   **User Tracking**: Automatic tracking of who created or modified any record.
*   **Audit Trail**: Detailed change history for critical models (batches, sales, customers).
*   **Soft Deletes**: Sales and expenses are archived instead of permanently deleted, with restore capability.
*   **Mobile-First Design**: Responsive UI built with Tailwind CSS.
*   **Dynamic UX**: HTMX integration for modal forms and autocompletes without page reloads.

## Quick Start

### Prerequisites
*   Python 3.10+
*   PostgreSQL (recommended) or SQLite (dev)

### Installation

1.  **Clone the repository** (if applicable)

2.  **Create a virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**
    Copy `.env.example` to `.env` and update the values:
    ```bash
    cp .env.example .env
    ```
    Set `DEBUG=True` for local development.

5.  **Run Migrations**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **Create Superuser**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Run Server**
    ```bash
    python manage.py runserver
    ```

## App Structure

*   `apps/core`: Base models, middleware, and common utilities.
*   `apps/accounts`: Custom user model and authentication.
*   `apps/customers`: Customer management with purchase history.
*   `apps/batches`: Jerrycan tracking and production output.
*   `apps/sales`: Transaction recording, payments, and invoices.
*   `apps/expenses`: Business expense tracking.

## Key Design Decisions

*   **Signals**: Used for audit logging and keeping payment statuses in sync.
*   **Middleware**: `UserTrackingMiddleware` ensures every action is attributed to a user.
*   **Templates**: Base template uses Alpine.js for the sidebar and HTMX for interactions.
