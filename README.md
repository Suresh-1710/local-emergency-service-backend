# Local Emergency Service Connect — Backend

FastAPI backend for a two-sided marketplace connecting clients with nearby plumbers, electricians, and carpenters.

## How it works

1. A **client** posts a job — category, description, photo, and location.
2. The address is geocoded into coordinates automatically.
3. Nearby **workers** in that trade (within 5km, calculated with the Haversine formula) see the job on their dashboard.
4. The first worker to accept locks the job — no one else can take it.
5. The **client** (not the worker) confirms the job is completed, preventing a worker from falsely marking their own work done.

## Tech stack

FastAPI, PostgreSQL, SQLAlchemy, JWT auth, Cloudinary (photo storage), Nominatim (geocoding).

## Running locally

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create a `.env` file with:

```
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<db_name>
SECRET_KEY=<a random secret string>
CLOUDINARY_CLOUD_NAME=<your cloudinary cloud name>
CLOUDINARY_API_KEY=<your cloudinary api key>
CLOUDINARY_API_SECRET=<your cloudinary api secret>
```

Run `schema.sql` against your database to create the tables, then start the server:

```bash
python -m uvicorn main:app
```

## Key design decisions

- **Clients and workers are separate entities** with separate signup/login, not a single user table with a role flag.
- **Race-condition-safe job acceptance**: accepting a job takes a database row lock, so two workers clicking "Accept" at the same instant can't both win.
- **Photos are stored on Cloudinary, not the app server** — the server's disk is not persisted across deploys/restarts on most hosting platforms, so photos live externally and the database just stores the URL.
