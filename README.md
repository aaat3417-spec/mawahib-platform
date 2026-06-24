# Mawahib Community Platform

A production-ready community platform for gifted students. It includes task management, submissions, review workflows, points, badges, teams, leaderboards, announcements, notifications, dashboards, profile portfolios, admin statistics, PostgreSQL migrations, Docker Compose, Nginx, JWT auth, role permissions, upload validation, rate limiting, and local file storage.

## Stack

- Frontend: React, Vite, Tailwind CSS, React Router, Axios
- Backend: FastAPI, SQLAlchemy, Pydantic, JWT authentication
- Database: PostgreSQL
- Deployment: Docker Compose and Nginx
- Storage: local `uploads/` directory

## Structure

```text
backend/
  app/
    core/ db/ middleware/ models/ permissions/ routes/ schemas/ services/
  migrations/
frontend/
  src/
    components/ hooks/ layouts/ pages/ services/ styles/
nginx/
scripts/
uploads/
```

## Quick Start

1. Copy the environment template:

```bash
cp .env.example .env
```

2. Edit `.env` and replace `SECRET_KEY`, `POSTGRES_PASSWORD`, and `DATABASE_URL`. In production, also set `ENVIRONMENT=production`, `ALLOWED_HOSTS` to your real hostnames, `CORS_ORIGINS` to your real frontend origins, and `DOCS_ENABLED=false`.

3. Start the platform:

```bash
docker compose up --build
```

4. Open the app:

```text
http://localhost:8080
```

The backend runs migrations automatically during container startup. If `INITIAL_OWNER_EMAIL` and `INITIAL_OWNER_PASSWORD` are set, the first owner account is seeded automatically. You can also use the "First owner" tab on the login page if the database has no users.

## Local Development

Backend:

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://mawahib:mawahib@localhost:5432/mawahib
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api` and `/uploads` to `http://localhost:8000`.

## Render Deployment

For the free Render test deployment, use the dedicated guide at `outputs/render-deployment-guide.md`.
The backend can run with SQLite using `DATABASE_URL=sqlite:///./mawahib.db`; SQLite tables are created automatically on startup, so Render should use `sh start_render.sh` instead of running Alembic migrations.

## Roles and Permissions

- Owner: full platform control, including owner/admin accounts.
- Admin: manages users, teams, tasks, announcements, submissions, and statistics.
- Team Leader: creates tasks and reviews submissions for their team.
- Student: joins teams, completes tasks, uploads achievements, earns points, and tracks progress.

## Point Rules

- Task completion: task points, default `100`
- Excellent work: `+50`
- Optional task bonus: `+30`
- Helping members: `+20`
- Late submission: `-20`

## Security Features

- Bcrypt password hashing
- JWT bearer authentication
- Role-based access guards
- Upload validation for PDF and image files
- File signature checks for declared upload types
- Configurable upload size limit
- In-process rate limiting
- Trusted Host middleware
- Production checks for unsafe secrets and wildcard hosts/origins
- Structured FastAPI logging
- Nginx reverse proxy

## Backups

Run:

```bash
sh scripts/backup.sh
```

The script writes a PostgreSQL dump and compressed upload archive into `backups/`.

## Main API Areas

- `POST /api/auth/login`
- `POST /api/auth/setup-owner`
- `GET /api/statistics/dashboard`
- `GET /api/tasks`
- `POST /api/tasks`
- `POST /api/submissions/tasks/{task_id}`
- `PATCH /api/submissions/{submission_id}/review`
- `GET /api/leaderboard/students`
- `GET /api/leaderboard/teams`
- `GET /api/announcements`
- `GET /api/users/me/profile`
- `GET /api/statistics/overview`
