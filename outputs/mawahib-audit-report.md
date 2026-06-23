# Mawahib Community Platform Audit Report

Date: 2026-06-23  
Role: Senior QA Engineer and Senior Software Architect

## Executive Summary

The project was reviewed across backend security, API behavior, permissions, database design, frontend workflows, responsiveness, and Docker/Nginx deployment. Multiple production-readiness issues were found and fixed, especially around role boundaries, upload validation, point-award idempotency, UTC time handling, deployment hardening, and admin feature completeness.

Current status: improved and hardened for production deployment. Final container/runtime validation still needs to be run on a host with Docker and npm registry access.

## High-Impact Fixes Completed

### Security

- Added production configuration validation.
- Production now rejects unsafe default `SECRET_KEY`.
- Production now rejects wildcard CORS origins.
- Production now rejects wildcard trusted hosts.
- Production now rejects enabled API docs through `DOCS_ENABLED=true`.
- Added `TrustedHostMiddleware`.
- Added Nginx security headers:
  - `X-Content-Type-Options`
  - `X-Frame-Options`
  - `Referrer-Policy`
  - `Permissions-Policy`
- Added non-root backend container user.
- Added password strength validation.
- Capped password length at 72 characters to avoid bcrypt truncation/compatibility issues.
- Added upload file signature validation for PDF/JPEG/PNG/WebP.
- Rejected empty uploads.
- Added HTTP(S) validation for submission links and task attachment URLs.
- Restricted GitHub submissions to `github.com`.

### Backend Bugs

- Replaced naive UTC usage with timezone-aware UTC helpers.
- Fixed late-submission comparison risk caused by mixed naive/aware datetimes.
- Fixed dashboard progress to count accepted required tasks distinctly.
- Fixed completed task count to count distinct tasks, not duplicate accepted submissions.
- Fixed leaderboard period filtering so weekly/monthly rankings do not accidentally exclude users or distort joins.
- Fixed team leaderboard period aggregation.
- Fixed accepted review recalculation by clearing prior submission point events before re-awarding.
- Prevented duplicate helping-member points for the same submission.
- Prevented duplicate accepted notifications on re-review.
- Fixed latest task submission status display by preserving newest submission status.
- Fixed owner setup email normalization.
- Fixed profile point event count to use aggregate queries instead of loading full histories.
- Updated broken `psycopg[binary]` dependency pin from `3.2.3` to resolvable `3.2.13`.

### Permission Issues

- Admins can no longer create or manage owner/admin accounts unless they are owners.
- Owners cannot accidentally deactivate or demote the last active owner.
- Users cannot deactivate themselves.
- Users cannot change their own role.
- Admin point adjustments against owner/admin accounts now require owner role.
- Inactive users cannot receive point adjustments.
- Team leaders can only edit/delete tasks they created.
- Team leaders cannot review submissions outside their team.
- Team leaders cannot review their own submissions.
- Only students can self-join teams.
- Owners/admins cannot be assigned as team leaders.
- Team leader assignment now clears previous leader links safely.

### Database Design and Performance

- Added indexes for hot paths:
  - `teams.leader_id`
  - `submissions.student_id/task_id/status`
  - `points.user_id/created_at`
  - `points.submission_id/reason`
  - `notifications.user_id/read_at/created_at`
- Updated the initial migration to include the same indexes.
- Improved aggregate queries for rankings, dashboards, and profile statistics.

### Frontend Issues

- Added admin management surfaces for:
  - Users
  - Teams
  - Tasks
  - Announcements
- Added inline user edits for role/team/active status/name.
- Added inline task edits for title, points, deadline, and required status.
- Added announcement editing, pin/unpin, and delete controls.
- Fixed review modal to preload the current submission status and feedback.
- Added scrollable modal behavior for mobile screens.
- Matched frontend password max length to backend bcrypt-safe limit.
- Improved admin feedback handling for failed promotion and management actions.

### Docker and Nginx

- Docker Compose now requires database secrets instead of silently using weak defaults.
- Added backend health check.
- Added restart policies.
- Nginx now waits for backend health.
- Backend container now runs as a non-root user.
- Backend starts Uvicorn with proxy headers enabled.
- README now documents Python 3.12 target and production security settings.

## Verification Performed

Passed:

```bash
PYTHONPYCACHEPREFIX=work/pycache python3 -m compileall -q backend/app backend/migrations
```

Passed:

```bash
node --check frontend/vite.config.js
node --check frontend/tailwind.config.js
node --check frontend/postcss.config.js
```

Passed:

```bash
rg -n "TODO|FIXME|datetime\.utcnow|date\.today|psycopg\[binary\]==3\.2\.3|console\.log|debugger|latest" backend frontend docker-compose.yml nginx README.md .env.example -g '!work/**'
```

The search returned no actionable matches.

## Verification Not Completed Locally

- `docker compose config` could not run because Docker is not installed in this environment.
- Frontend dependency install/build could not complete because `npm install` stalled in the local environment.
- Backend runtime import checks could not be fully executed on the local Python because the project targets Docker Python 3.12, while local Python is 3.9.6 and lacks required installed dependencies.

## Recommended Production Smoke Test

Run on a machine with Docker and npm registry access:

```bash
cp .env.example .env
```

Edit `.env`:

```text
ENVIRONMENT=production
DOCS_ENABLED=false
SECRET_KEY=<long-random-secret>
POSTGRES_PASSWORD=<strong-password>
DATABASE_URL=postgresql+psycopg://mawahib:<strong-password>@db:5432/mawahib
ALLOWED_HOSTS=<your-domain>
CORS_ORIGINS=https://<your-domain>
```

Then run:

```bash
docker compose config
docker compose up --build
```

Smoke-test:

```bash
curl http://localhost:8080/health
```

Then verify:

- Owner account can log in.
- Admin can create a student.
- Student can join a team.
- Admin/team leader can create a task.
- Student can submit a PDF/image/link/GitHub URL.
- Team leader can review only own-team submissions.
- Accepted submission awards points exactly once.
- Re-review from accepted to rejected removes prior submission points.
- Dashboard progress and leaderboard update correctly.

## Residual Risks

- The in-memory rate limiter is acceptable for a single backend instance, but production multi-replica deployments should move rate limiting to Redis or the edge proxy.
- Local uploads are suitable for one host. Multi-host production should move uploads to object storage or shared persistent storage.
- The project still needs CI with Docker build, frontend build, backend import/startup checks, and API integration tests.
- A generated `package-lock.json` should be committed after npm registry access is available.

## Final Assessment

The platform is significantly more production-ready after this audit pass. The most important security and correctness risks have been addressed in code. Remaining work is operational validation in a Docker-enabled environment and adding CI/integration tests.

