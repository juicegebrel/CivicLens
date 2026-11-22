# CivicLens

Progress monitoring for Local Development Fund (LDF) projects. Barangays and constituents can see project status online instead of visiting the CPDO.

## Features
- **Public dashboard** with a status donut, KPIs, per-category stacked bars and latest updates. It refreshes itself every 30 seconds from `/api/stats/`.
- **Project search** by keyword and category, with status and barangay filters.
- **Status checker** at `/check/`: enter a reference code (e.g. `LDF-2026-0001`).
- **Login**: barangay accounts see their own projects at `/my-projects/`; CPDO staff see all projects and can post status updates, which appear in each project's public history.
- **Django admin** at `/admin/` to encode projects, barangays, categories and accounts.

## Project structure
Only the feature apps live in `apps/`. Settings, templates and static files stay at the project root, grouped per app.
```
config/              settings, root URLs, wsgi
apps/
  projects/          models, admin, seed_demo; search, detail and update-status screens
  dashboard/         home dashboard, infographics and /api/stats/
  statuscheck/       public status checker (/check/)
  accounts/          login, logout, register, "My projects", barangay profile
templates/           base.html, then one folder per app (templates/projects/, ...)
static/css/          civiclens.css (shared), then css/<app>/<app>.css
static/js/           js/<app>/<app>.js
```

## Setup
```
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations accounts projects
python manage.py migrate
python manage.py seed_demo       # optional demo data
python manage.py runserver
```
Open http://127.0.0.1:8000/

Demo accounts (created by `seed_demo`): `cpdo` (staff) and `brgy_lahug` (Barangay Lahug), both with password `civiclens123`. Change these before any real use.

To create a real admin: `python manage.py createsuperuser`. To link a barangay account, open the user in the admin and set the Barangay in the Profile section.

Run tests: `python manage.py test`

## Deploying
Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0` and `DJANGO_ALLOWED_HOSTS`, then run `python manage.py collectstatic` and serve with gunicorn plus a static file server (or WhiteNoise).
