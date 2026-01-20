# Wals Honey Management System 🍯

The **Wals Honey Management System** is a comprehensive solution designed to streamline honey inventory, sales, and expense tracking. It provides end-to-end visibility from batch acquisition to final sale, ensuring accurate inventory management and financial reporting.

## Key Features
- **Batch Tracking**: Precise tracking of honey batches, including source and individual jerrycan details.
- **Inventory Management**: Real-time stock levels and automated status updates.
- **Sales & Payment Tracking**: Transaction recording with partial payment support, customer auto-creation, and complete payment history.
- **Financial Tracking**: Expense logging and financial health monitoring.
- **Audit Trail**: Detailed logging of all critical actions for accountability.
- **Mobile-First Design**: Optimized for use on tablets and mobile devices in the field.

## Quick Start
Get the system up and running in minutes:

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd wals-honey-mgmt
    ```

2.  **Set up the environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Configure environment variables:**
    Copy `.env.example` to `.env` and set your secret key and database settings.

4.  **Initialize the database:**
    ```bash
    python manage.py migrate
    python manage.py createsuperuser
    ```

5.  **Run the server:**
    ```bash
    python manage.py runserver
    ```

## Documentation
For more detailed information, please refer to the documentation:
- [Setup Guide](docs/setup.md)
- [Architecture Overview](docs/architecture.md)
- [Business Logic & Workflows](docs/business_logic.md)
- [Deployment Guide](docs/deployment.md)

## Testing
The project includes comprehensive unit tests:

```bash
# Run all tests
python manage.py test

# Run specific module tests
python manage.py test apps.batches.tests    # 72 tests
python manage.py test apps.sales.tests      # 25 tests
```

| Module | Tests | Coverage |
|--------|-------|----------|
| Batches | 72 | Models, Forms, Views, Edge Cases |
| Payments | 25 | Form validation, Views, Status updates |

## Tech Stack
- **Backend**: Django (Python)
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **Frontend**: Django Templates, Vanilla CSS/JS, HTMX (for dynamic interactions)
- **Deployment**: Render.com, Supabase(Might go with a different option at deployment stage)

## Team
Developed by the Walid Mahmud.

## License
Proprietary software. All rights reserved.
