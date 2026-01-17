# Setup Guide

This guide provides step-by-step instructions to set up the Wals Honey Management System for local development.

## Prerequisites
- **Python**: Version 3.10 or higher.
- **Git**: For version control.
- **pip**: Python package installer.
- **Virtual Environment**: Recommended to isolate dependencies.

## Installation Steps

### 1. Clone the Repository
```bash
git clone <repository_url>
cd wals-honey-mgmt
```

### 2. Create and Activate Virtual Environment
It's best practice to run Python projects in a virtual environment.
```bash
# multiple operating systems
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install Dependencies
Install the required Python packages listed in `requirements.txt`.
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory by copying the example file.
```bash
cp .env.example .env
```
Open `.env` and configure the following variables:
- `SECRET_KEY`: A secure random string for Django security.
- `DEBUG`: Set to `True` for development.
- `DATABASE_URL`: (Optional) Use SQLite by default, or configure for PostgreSQL.

### 5. Database Setup
Apply migrations to set up the database schema.
```bash
python manage.py migrate
```

### 6. Create Superuser
Create an administrative account to access the Django Admin interface.
```bash
python manage.py createsuperuser
```
Follow the prompts to set a username, email, and password.

### 7. Run the Development Server
Start the local server.
```bash
python manage.py runserver
```
You should see output indicating the server is running at `http://127.0.0.1:8000/`.

## Verifying Installation
1. Open your browser and navigate to `http://127.0.0.1:8000/`.
2. Log in with the superuser credentials you created.
3. You should see the main dashboard.
4. Navigate to `/admin/` to verify admin access.

## Common Issues
- **Database Errors**: Ensure you have run `migrate`.
- **Static Files**: If styles are missing, check if `DEBUG=True` in `.env`.
- **Port In Use**: If port 8000 is taken, run with a different port: `python manage.py runserver 8081`.

## Next Steps
Once set up, refer to the [Architecture Overview](architecture.md) to understand the system structure or [Business Logic](business_logic.md) to learn about the workflows.
