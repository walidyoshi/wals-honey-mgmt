# Project Structure

This document outlines the file structure of the **Wals Honey Management System** and provides an explanation of its components.

## Directory Tree

```text
.
├── apps
│   ├── accounts
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   ├── models.py
│   │   ├── templates
│   │   ├── urls.py
│   │   └── views.py
│   ├── batches
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   ├── models.py
│   │   ├── signals.py
│   │   ├── templates
│   │   ├── urls.py
│   │   └── views.py
│   ├── core
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── middleware.py
│   │   ├── models.py
│   │   └── templatetags
│   ├── customers
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   ├── models.py
│   │   ├── templates
│   │   ├── urls.py
│   │   └── views.py
│   ├── expenses
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   ├── models.py
│   │   ├── templates
│   │   ├── urls.py
│   │   └── views.py
│   ├── __init__.py
│   └── sales
│       ├── admin.py
│       ├── apps.py
│       ├── forms.py
│       ├── __init__.py
│       ├── migrations
│       ├── models.py
│       ├── signals.py
│       ├── templates
│       ├── urls.py
│       └── views.py
├── config
│   ├── asgi.py
│   ├── __init__.py
│   ├── settings
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── __init__.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3
├── manage.py
├── README.md
├── requirements.txt
├── static
│   ├── css
│   │   └── custom.css
│   └── js
│       └── main.js
└── templates
    ├── base.html
    └── partials
        ├── change_history.html
        └── sidebar_nav.html
```

## Structure Explanation

This is a modular **Django** project structure designed for scalability and separation of concerns.

### Root Directory
- **`manage.py`**: The standard Django command-line utility for administrative tasks (running server, migrations, etc.).
- **`requirements.txt`**: Lists the Python dependencies for the project.
- **`README.md`**: Project overview and setup instructions.
- **`db.sqlite3`**: Examples of a local SQLite database (typically replaced by PostgreSQL in production).

### `config/` (Configuration)
Contains the project-level configuration.
- **`settings/`**: Settings are split into environments:
    - `base.py`: Common settings (installed apps, middleware, tempaltes).
    - `development.py`: Local dev specific settings (debug mode).
    - `production.py`: Production settings (security, database config).
- **`urls.py`**: The root URL configuration that routes requests to the specific apps.
- **`wsgi.py` / `asgi.py`**: Entry points for web servers to serve the application.

### `apps/` (Modules)
The business logic is divided into separate Django "apps":

1.  **`core`**: Contains base functionality shared across the system.
    - `middleware.py`: Custom middleware (e.g., user tracking).
    - `models.py`: Abstract base models (e.g., `TimeStampedModel`).
2.  **`accounts`**: User management.
    - Custom user models and authentication logic.
3.  **`batches`**: Inventory and production tracking.
    - Managing Jerrycans and honey production batches.
4.  **`customers`**: CRM features.
    - Managing customer data and history.
5.  **`sales`**: Logic for transactions.
    - Managing sales records, payments, and generated signals (audit logs).
6.  **`expenses`**: Financial tracking.
    - Tracking business expenses.

### `static/` & `templates/`
- **`static/`**: Global static assets (CSS, JS) used across the site.
- **`templates/`**: Global HTML templates.
    - `base.html`: The master layout extended by other pages.
    - `partials/`: Reusable HTML fragments (often used with HTMX).
