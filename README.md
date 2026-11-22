# CivicLens

Progress monitoring for Local Development Fund (LDF) projects. Barangays and constituents can see project status online instead of visiting the CPDO.

## Data model (follows the project ERD)
- **User**: Django's built-in user (first name, last name, email, password).
- **CityOfficial**: links a user to the city (CPDO). Can update the status of any project.
- **BarangayOfficial**: links a user to one **Barangay**.
- **Barangay**: name plus a randomly generated `barangay_code` (e.g. `K7M2-QX9T`). Officials need this code to register.
- **Project**: name, status, amount, project date.
- **BarangayProject**: which barangay(s) a project serves, and the **sitio**. One project can serve several barangays.

## Features
- **Public dashboard**: status donut, total money allocated, money tapped (projects that are awarded, in process or completed), projects per barangay and latest projects. Refreshes itself every 30 seconds from `/api/stats/`.
- **Project search** by keyword (project, barangay or sitio), status and barangay.
- **Status checker** at `/check/`: enter a reference code such as `LDF-0001`.
- **Register** at `/accounts/register/`: a barangay official enters the barangay's code and is linked to that barangay automatically.
- **My projects**: barangay officials see their barangay's projects; city officials see all.
- **Django admin** at `/admin/`: add projects (with barangays and sitios), barangays and accounts. Open a barangay to see its registration code, or use the "Generate a new registration code" action to replace it.

## Project structure
Only the feature apps live in `apps/`. Settings, templates and static files stay at the project root, grouped per app.
```
config/              settings, root URLs, wsgi
apps/
  projects/          Barangay, Project, BarangayProject; search, detail, update-status; seed_demo
  dashboard/         home dashboard and /api/stats/
  statuscheck/       public status checker (/check/)
  accounts/          CityOfficial, BarangayOfficial; register, login, My projects
templates/           base.html, then one folder per app
static/css/          civiclens.css (shared), css/<app>/<app>.css
static/js/           js/<app>/<app>.js
```

## Setup
```
python -m venv .venv
.venv\Scripts\activate           # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo       # optional demo data; prints each barangay's code
python manage.py runserver
```
Open http://127.0.0.1:8000/

Demo accounts from `seed_demo`: `cpdo` (city official and admin) and `brgy_lahug` (Barangay Lahug). Their password is `civiclens123` unless you set the `CIVICLENS_DEMO_PASSWORD` environment variable first. Change these before any real use.

To make a real admin: `python manage.py createsuperuser`, then in `/admin/` add a **City official** entry for that user so they can update project status.

Run tests: `python manage.py test`

## Deploying
Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0` and `DJANGO_ALLOWED_HOSTS`, then run `python manage.py collectstatic` and serve with gunicorn plus a static file server (or WhiteNoise).

## Contributing
Commits follow [Conventional Commits](https://www.conventionalcommits.org/). See `CONTRIBUTING.md`, and enable the commit-msg check with `git config core.hooksPath .githooks`.
