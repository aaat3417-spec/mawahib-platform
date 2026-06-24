# Render Deployment Guide

This guide deploys Mawahib Community Platform on Render with SQLite for free-plan testing.

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

The start script runs `python -m app.db.init_db` before `uvicorn`. SQLite tables are created automatically because `DATABASE_URL` starts with `sqlite`. Alembic is intentionally not run for SQLite free-plan deployments because SQLite cannot apply every ALTER/constraint migration safely.

### Backend Environment

```text
DATABASE_URL=sqlite:///./mawahib.db
PYTHON_VERSION=3.11.11
SECRET_KEY=replace-with-a-long-random-secret-key
INITIAL_OWNER_EMAIL=owner@mawahib.com
INITIAL_OWNER_PASSWORD=ChangeMe123!
CORS_ORIGINS=["http://localhost:5173","http://localhost:8080","https://mawahib-platform-1.onrender.com"]
ALLOWED_HOSTS=localhost,127.0.0.1,mawahib-platform.onrender.com,mawahib-platform-1.onrender.com
DOCS_ENABLED=true
ENVIRONMENT=development
```

Production note: replace `SECRET_KEY` with a long random value before real use.

### Backend Checks

```text
https://mawahib-platform.onrender.com/
https://mawahib-platform.onrender.com/health
https://mawahib-platform.onrender.com/docs
```

Expected health response:

```json
{"status":"ok","service":"Mawahib Community Platform"}
```

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

### Frontend Environment

```text
VITE_API_URL=https://mawahib-platform.onrender.com
```

This value is required so the deployed Vite app calls the deployed FastAPI service instead of using local `/api`.

### Frontend React Router Rewrite

For an existing manually-created Render Static Site, add this rule in the frontend service:

```text
Settings -> Redirects/Rewrites -> Add Rule
Source: /*
Destination: /index.html
Action: Rewrite
```

This is required for direct refreshes on routes such as `/leaderboard`, `/tasks`, `/profile`, and `/admin`.
Without it, Render serves `Not Found` because the React app owns those routes in the browser.

## Login Test

Open:

```text
https://mawahib-platform-1.onrender.com
```

Login with:

```text
owner@mawahib.com
ChangeMe123!
```

Expected result: login succeeds without Network Error, CORS error, Invalid host header, or missing database table errors.
