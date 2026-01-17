# Deployment Guide

This document outlines the steps to deploy the Wals Honey Management System to production using **Render.com** (hosting) and **Supabase** (database).

## Prerequisites
-   **Render Account**: Create one at [render.com](https://render.com).
-   **Supabase Account**: Create one at [supabase.com](https://supabase.com).
-   **Git Repository**: Code pushed to GitHub/GitLab.

## Environment Variables
The following environment variables must be configured in your production environment:

| Variable | Description |
| :--- | :--- |
| `SECRET_KEY` | Large random string for cryptographic signing. |
| `DEBUG` | **Must be False** in production. |
| `ALLOWED_HOSTS` | Domain name of your Render app (e.g., `wals-honey.onrender.com`). |
| `DATABASE_URL` | Connection string from Supabase (postgres://...). |
| `DJANGO_SETTINGS_MODULE` | Set to `config.settings.production`. |

## Step 1: Database Setup (Supabase)
1.  **Create Project**: Log in to Supabase and create a new project.
2.  **Get Credentials**:
    -   Go to **Project Settings** -> **Database**.
    -   Copy the **Connection String** (use the "URI" format).
    -   Ideally, it looks like: `postgres://postgres:[YOUR-PASSWORD]@db.project-ref.supabase.co:5432/postgres`

## Step 2: Render Deployment
1.  **Create Web Service**:
    -   Log in to Render dashboard.
    -   Click "New +" -> "Web Service".
    -   Connect your GitHub repository.
2.  **Configure Service**:
    -   **Name**: `wals-honey-mgmt`
    -   **Environment**: `Python 3`
    -   **Build Command**: `./build.sh` (You may need to create this script, see below) OR:
        ```bash
        pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
        ```
    -   **Start Command**: `gunicorn config.wsgi:application`
3.  **Environment Variables**:
    -   Add all variables listed in the section above.
    -   Paste your Supabase `DATABASE_URL`.

## Step 3: First Deployment Checklist
Once the build finishes and the service is live:
1.  **Create Superuser**:
    -   Go to the "Shell" tab in Render.
    -   Run: `python manage.py createsuperuser`
2.  **Verify Static Files**:
    -   Check if CSS/JS loads correctly. (WhiteNoise should handle this).
3.  **HTTPS**:
    -   Render automatically provisions an SSL certificate. Verify the URL is `https://`.

## Maintenance & Monitoring
-   **Logs**: Check the "Logs" tab in Render for errors.
-   **Backups**: Enable "Point in Time Recovery" (PITR) in Supabase for database backups.
-   **Performance**: Use Supabase's dashboard to monitor query performance.

## Troubleshooting
-   **"Relation does not exist"**: You forgot to run `python manage.py migrate`.
-   **Server Error (500)**: Check `DEBUG=False` allows standard error pages. Check logs for the real stack trace.
-   **CSS Missing**: Ensure `whitenoise` is in your `requirements.txt` and `MIDDLEWARE` settings.
