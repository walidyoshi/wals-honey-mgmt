# Project Structure

This document outlines the file structure of the **Wals Honey Management System** and provides an explanation of its components.

## Directory Tree

```text
.
├── apps
│   ├── accounts          # Authentication & User Management
│   ├── batches           # Inventory & Honey Batch Tracking
│   ├── core              # Shared Utilities & Middleware
│   ├── customers         # Customer Data
│   ├── expenses          # Business Expense Tracking
│   └── sales             # Transactions & Payment Logic
├── config
│   ├── settings          # Environment-specific settings
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py           # Main URL routing
│   └── wsgi.py           # Server entry point
├── docs                  # Detailed Documentation
├── static                # Global Static Files (CSS/JS)
├── templates             # Global HTML Templates
├── db.sqlite3            # Local Development Database
├── manage.py             # Django CLI Utility
├── README.md             # Project Overview
├── requirements.txt      # Python Dependencies
└── STRUCTURE.md          # This File
```

## Structure Explanation

This is a modular **Django** project structure designed for scalability and separation of concerns.

### Root Directory
- **`manage.py`**: The standard Django command-line utility for administrative tasks.
- **`requirements.txt`**: Lists the Python dependencies for the project.
- **`docs/`**: Contains detailed documentation for setup, architecture, and deployment.

### `config/` (Configuration)
Contains the project-level configuration, distinct from the apps.
- **`settings/`**: Settings are split to support clean development vs. production environments without complex logic switches.
- **`urls.py`**: The central traffic controller that dispatches requests to the appropriate app.

### `apps/` (Modules)
The business logic is strictly divided into separate apps. This "modular monolith" approach prevents spaghetti code.

1.  **`core`**: The "glue" of the system.
    -   Contains code that doesn't fit into a specific domain (e.g., `TimeStampedModel`, `UserTrackingMiddleware`).
2.  **`accounts`**: Custom user model and auth logic. Separation allows for future expansion (e.g., different user types).
3.  **`batches`**: The heart of the inventory system. Manages the lifecycle of honey from supplier to sale.
4.  **`customers`**: Manages entity relationships. Kept separate so it can be reused by Sales or other future modules.
5.  **`sales`**: Handles the point-of-sale logic. Dependent on `customers` and `batches` but manages its own transaction state.
6.  **`expenses`**: A standalone module for tracking costs, enabling financial reporting.

### `static/` & `templates/`
These directories hold *global* assets. App-specific templates are usually kept within `apps/<app_name>/templates`, but global layouts (`base.html`) live here.
