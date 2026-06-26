# P0 Production Incident Response Report

Date: 2026-06-27

## Incidents

P0 #1: Data disappeared after hours/restarts.

Most likely root cause:
- Production was previously operating on SQLite in Render instance storage or an inconsistent SQLite working-directory path.
- Instance-local SQLite files can disappear after restart, redeploy, rebuild, or host move.

Architectural fix:
- `render.yaml` now provisions `mawahib-postgres`.
- Backend `DATABASE_URL` now comes from the Render PostgreSQL connection string.
- `start_render.sh` runs Alembic migrations before safe initialization when the database is not SQLite.
- SQLite remains supported only for local/demo use.
- Production SQLite with a non-`/var/data` path is blocked by settings validation.
- Uploads remain on Render Persistent Disk at `/var/data/uploads`.

P0 #2: User reported seeing another user's page.

Most likely contributing cause:
- Frontend previously initialized auth state from `localStorage.mawahib_user` before confirming identity with `/api/auth/me`.
- That can briefly show stale user data after logout/login or browser back.

Fix:
- Frontend now stores only the token.
- `/api/auth/me` is the source of truth for user identity.
- Login/setup clear previous token/user state before requesting a new token.
- Logout clears token/user state and emits a logout event.
- API responses now include no-store headers.
- Backend profile access now prevents team leaders from viewing profiles outside their team.
- Student IDOR checks were verified: student B cannot fetch student A profile.

## New Registration System

Implemented team-code registration:
- Each team has `team_code`.
- Each team has `is_code_active`.
- Admin can list team codes, copy codes, regenerate codes, and enable/disable codes.
- New users submit join requests through `POST /api/registration/request`.
- Passwords are hashed immediately; plain passwords are never stored.
- Admin can accept, reject, or request changes.
- Accepted requests create active student users in the selected team.
- Pending or rejected requests cannot login.

New backend endpoints:
- `POST /api/registration/request`
- `GET /api/admin/registration-requests`
- `POST /api/admin/registration-requests/{id}/accept`
- `POST /api/admin/registration-requests/{id}/reject`
- `POST /api/admin/registration-requests/{id}/request-changes`
- `GET /api/admin/teams`
- `POST /api/admin/teams/{id}/regenerate-code`
- `PATCH /api/admin/teams/{id}/code-status`
- `GET /api/admin/data-health`
- `GET /api/admin/export`

## Verification

Passed local backend verification:
- Created a team.
- Confirmed team code exists.
- Created three direct users.
- Created a task.
- Created an announcement.
- Registration with wrong code returned `404`.
- Registration with valid code created `Pending` request.
- Login before admin acceptance returned `401`.
- Duplicate pending request returned `409`.
- Admin accepted request.
- Accepted user login succeeded.
- Admin rejected another request.
- Rejected user login returned `401`.
- User A `/auth/me` returned A.
- After logging in as user B, `/auth/me` returned B.
- User B fetching user A profile returned `403`.
- User B fetching admin data health returned `403`.
- Admin data health returned correct counts.
- Admin export returned users/teams/tasks/announcements/registration requests and did not include `hashed_password`.

Restart persistence test:
- Restarted backend with the same SQLite test database.
- Verified data remained:
  - users: 5
  - teams: 6
  - tasks: 1
  - announcements: 1
  - registration_requests: 2
  - team codes still present: true

Build/compile:
- `python -m compileall -q backend/app backend/migrations backend/init_db.py scripts/export_data.py`
- `npm run build`

## Direct Production Answers

Does production use PostgreSQL now?
- The repository blueprint now does. The live Render service must be redeployed from this commit or manually changed to use PostgreSQL.

Is SQLite still used?
- Only for local/demo testing. It is not the production path.

Is a Persistent Disk still needed?
- Yes, for uploads under `/var/data/uploads`.
- No, PostgreSQL no longer stores database rows on the disk.

Can data loss repeat?
- If the live Render backend is deployed with this PostgreSQL configuration, database-row loss from instance restarts should not repeat.
- If Render is manually left on `sqlite:///./mawahib.db`, data loss can repeat.

Can the user-mixup repeat?
- The known stale-localStorage cause has been removed.
- Backend IDOR checks were verified for student-to-student profile access and admin endpoint access.
