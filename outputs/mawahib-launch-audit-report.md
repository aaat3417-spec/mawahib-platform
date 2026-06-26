# Mawahib Launch Audit Report

Date: 2026-06-26

## Executive Summary

The platform is materially safer and more usable after this pass. The most likely cause of the reported user disappearance was Render SQLite data stored on instance-local storage instead of a Persistent Disk. The backend seed path was reviewed and does not drop tables or delete users; the deployment configuration now stores SQLite and uploads under `/var/data`.

For real production with real students, use PostgreSQL. The current Render blueprint now provisions PostgreSQL as the primary production database. SQLite is acceptable only for testing or demos when backed by a Persistent Disk.

## P0 Data Loss

Likely cause:
- Render was previously configured with `sqlite:///./mawahib.db`, which stores the DB inside ephemeral service storage.
- A restart, rebuild, deploy, or instance move can make that file disappear.

Fix:
- `render.yaml` now provisions a Render disk mounted at `/var/data`.
- Backend Render env now uses a PostgreSQL connection string from `mawahib-postgres`.
- Uploads now use `UPLOAD_DIR=/var/data/uploads`.
- `init_db` remains non-destructive and uses SQLAlchemy `create_all`, which creates missing tables only.
- Added a persistence warning if production SQLite is not under `/var/data`.
- Added `scripts/export_data.py` for read-only JSON exports.

Persistence test performed:
- Started FastAPI with SQLite at `work/qa-persistence-2.db`.
- Logged in as owner.
- Created a student.
- Created two tasks without attachments.
- Submitted one task with notes only.
- Stopped and restarted FastAPI with the same SQLite file.
- Verified users, tasks, and submissions still existed after restart.

Observed result:
- `usersAfterRestart=2`
- `tasksAfterRestart=2`
- `submissionsAfterRestart=1`

## Backend / API Fixes

- Tightened `INITIAL_OWNER_EMAIL` to `EmailStr` so invalid seeded owner emails fail early instead of corrupting response validation.
- Fixed backend settings loading so scripts and app startup read `backend/.env` consistently instead of accidentally reading a different `.env` from the current shell directory.
- Confirmed `/health`, `/`, and `/docs` return successfully in development mode.
- Confirmed duplicate email returns `409`.
- Confirmed task creation works with `attachments=[]`.
- Confirmed submission with notes only returns `Pending`.
- Confirmed `.js` upload is rejected with `400`.
- Confirmed authenticated file access remains protected by role checks.

## Frontend / UX Fixes

- Added centralized language provider with Arabic/English translations.
- Added language switch to login and authenticated layout.
- Persisted language choice in `localStorage`.
- Set `html.lang` and `html.dir` automatically.
- Confirmed Arabic changes `dir=rtl`.
- Confirmed mobile viewport has no horizontal overflow on login.
- Improved dashboard labels, dates, status labels, and statistics text.
- Improved task submission validation message and file-selected/remove-file state.
- Improved upload loading text.
- Added admin tabs for Users, Teams, Tasks, Announcements, Submissions, and Statistics.
- Added user search in Admin.
- Added admin password reset field per user.
- Added admin submissions section linking to review workflow.
- Improved translated success/error messages.

## Dates

- Dates now format through `Intl.DateTimeFormat`.
- Arabic uses Gregorian calendar locale `ar-SA-u-ca-gregory`.
- English uses concise Gregorian formatting.
- Dashboard weekday labels now use a dedicated weekday formatter instead of splitting date strings.
- `datetime-local` inputs continue to convert to ISO before backend submission.

## Security / RBAC Review

Confirmed existing protections:
- JWT bearer authentication.
- Password hashing with bcrypt.
- Role guards for owner/admin/team leader/student.
- Students cannot access admin APIs.
- Team leaders are scoped to their team for review/listing behavior.
- TrustedHost and CORS are explicit, not wildcard in production.
- Uploads reject dangerous extensions and validate file signatures.
- ZIP uploads reject path traversal and dangerous files.
- File downloads check ownership/team/admin access.

Remaining production recommendation:
- Keep real deployment on PostgreSQL before onboarding many real users.
- Disable docs in true production with `DOCS_ENABLED=false`.
- Rotate `SECRET_KEY` and owner password before real usage.
- Add automated test suite in CI; this repo currently has no dedicated test files.

## Verification Results

Passed:
- `npm run build`
- `python -m compileall -q backend/app backend/migrations backend/init_db.py scripts/export_data.py`
- Local FastAPI health/root/docs checks
- Owner login
- Create user
- Duplicate email rejection
- Create task without attachments
- Submit task with notes only
- Reject `.js` upload
- Restart persistence check
- JSON data export
- Mobile login viewport RTL/LTR and no horizontal overflow

Not performed:
- Full authenticated browser walkthrough against the deployed Render URLs, because this pass used the local build/API for deterministic verification.
- Real hosted PostgreSQL migration on Render, because credentials/deployment dashboard access are outside this local workspace.

## Direct Production Answer

For a real launch: use PostgreSQL. This is now the primary Render blueprint path.

If you stay on Render SQLite temporarily: you must use a Persistent Disk mounted at `/var/data`, with:

```text
DATABASE_URL=sqlite:////var/data/mawahib.db
UPLOAD_DIR=/var/data/uploads
```

SQLite without a Persistent Disk is not acceptable for real data.
