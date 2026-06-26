# Render Production Deployment Guide

This deployment guide treats PostgreSQL as the primary production database for Mawahib Community Platform.

## Backend Web Service

- Service type: Web Service
- Root Directory: `backend`
- Runtime: Python
- Build Command:

```bash
pip install -r requirements.txt
```

- Start Command:

```bash
sh start_render.sh
```

For PostgreSQL, `start_render.sh` runs:

```bash
alembic upgrade head
python -m app.db.init_db
uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
```

This is migration-safe: Alembic applies schema migrations and `init_db` only seeds missing defaults. It does not drop tables, delete users, reset passwords, or recreate existing records.

## Render PostgreSQL

Create a Render PostgreSQL database and connect it to the backend service.

Recommended backend environment:

```text
DATABASE_URL=<Render PostgreSQL internal connection string>
PYTHON_VERSION=3.11.11
ENVIRONMENT=production
DOCS_ENABLED=false
SECRET_KEY=<long generated secret>
INITIAL_OWNER_EMAIL=owner@mawahib.com
INITIAL_OWNER_PASSWORD=<strong first-login password>
UPLOAD_DIR=/var/data/uploads
CORS_ORIGINS=["http://localhost:5173","http://localhost:8080","https://mawahib-platform-1.onrender.com"]
ALLOWED_HOSTS=localhost,127.0.0.1,mawahib-platform.onrender.com,mawahib-platform-1.onrender.com
```

The included `render.yaml` now defines a PostgreSQL database named `mawahib-postgres` and injects its connection string into `DATABASE_URL`.

## Upload Disk

Even with PostgreSQL, uploaded files still need durable storage. Keep a Persistent Disk on the backend service:

```text
Name: mawahib-data
Mount Path: /var/data
Size: 1 GB or higher
```

Set:

```text
UPLOAD_DIR=/var/data/uploads
```

## SQLite Demo Only

SQLite is acceptable only for local/demo testing. On Render, SQLite must never use instance-local paths such as:

```text
sqlite:///./mawahib.db
```

If you temporarily test SQLite on Render, it must use Persistent Disk:

```text
DATABASE_URL=sqlite:////var/data/mawahib.db
UPLOAD_DIR=/var/data/uploads
ENVIRONMENT=development
DOCS_ENABLED=true
```

The backend now blocks `ENVIRONMENT=production` when SQLite is configured with a non-persistent path.

## Frontend Static Site

- Service type: Static Site
- Root Directory: `frontend`
- Build Command:

```bash
npm install && npm run build
```

- Publish Directory:

```text
dist
```

Frontend environment:

```text
VITE_API_URL=https://mawahib-platform.onrender.com
```

Add this Static Site rewrite for refresh-safe routes:

```text
Source: /*
Destination: /index.html
Action: Rewrite
```

The app also uses hash routing, so routes such as `/#/tasks` survive static hosting refreshes.

## Health and Data Checks

Public:

```text
https://mawahib-platform.onrender.com/health
```

Admin-only:

```text
GET /api/admin/data-health
GET /api/admin/export
```

`/api/admin/data-health` reports database type, masked database details, environment, uptime, startup time, and row counts for users, teams, tasks, submissions, announcements, and registration requests.

## Registration Requests

New student signup is now request-based:

```text
POST /api/registration/request
```

Admins manage requests:

```text
GET  /api/admin/registration-requests
POST /api/admin/registration-requests/{id}/accept
POST /api/admin/registration-requests/{id}/reject
POST /api/admin/registration-requests/{id}/request-changes
POST /api/admin/teams/{id}/regenerate-code
PATCH /api/admin/teams/{id}/code-status
```

Passwords for pending requests are hashed. Plain passwords are never stored.

## Troubleshooting

- Users disappear after restart: confirm the backend is using PostgreSQL. If testing SQLite, confirm `DATABASE_URL=sqlite:////var/data/mawahib.db` and that the disk is mounted at `/var/data`.
- Someone sees another user: clear old browser storage once, redeploy this version, then confirm `/api/auth/me` returns the correct user after every login. The frontend no longer trusts `mawahib_user` from localStorage.
- `Invalid host header`: confirm `ALLOWED_HOSTS` includes the backend and frontend Render domains.
- CORS/network error: confirm `CORS_ORIGINS` includes `https://mawahib-platform-1.onrender.com` and frontend `VITE_API_URL` points to the backend origin.
- Missing tables on PostgreSQL: confirm Start Command is `sh start_render.sh` so Alembic migrations run.
