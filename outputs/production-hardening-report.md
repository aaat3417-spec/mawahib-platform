# Mawahib Production Hardening Report

Date: 2026-06-24

## Scope

This pass reviewed and hardened the Render deployment path, FastAPI startup, CORS and host validation, authentication-dependent API flows, protected submission uploads, admin workflow gaps, frontend API configuration, mobile submission UX, and deployment documentation.

## Key Issues Found

- Submission files were exposed through public `/uploads` static hosting and returned internal storage paths to the frontend.
- Upload validation needed stronger extension, content-type, content signature, size, path traversal, and ZIP-safety checks.
- Mobile submission failures could be hidden behind the modal flow, making the green upload button appear broken.
- Render SPA refreshes could return `Not Found` without a static-site rewrite to `index.html`.
- Admin workflows were missing direct UI actions for awarding points and badges.
- Notifications displayed unread state but had no convenient "mark read" action in the layout.
- Production response headers were missing common browser hardening headers.
- Rate limiting did not prefer `X-Forwarded-For`, which matters behind Render proxies.

## Backend Fixes

- Added security headers middleware.
- Removed public static serving of the uploads directory.
- Added authenticated submission file downloads at `/api/submissions/{submission_id}/file`.
- Prevented submission responses from leaking stored filesystem paths.
- Added role-aware file authorization:
  - owners/admins can review relevant files,
  - team leaders can access files from their team,
  - students can access only their own files.
- Hardened upload storage:
  - random stored filenames,
  - safe original filename handling,
  - path traversal protection,
  - allowed types only: png, jpg, jpeg, pdf, txt, md, zip,
  - blocked script/executable extensions,
  - max upload size enforcement,
  - PDF/JPEG/PNG/ZIP signature checks,
  - UTF-8 checks for text uploads,
  - ZIP entry count, traversal, dangerous extension, and uncompressed size checks.
- Added `backend/init_db.py` as a safe wrapper for database initialization.
- Kept SQLite startup table creation compatible with Render free testing.
- Improved rate limiting client identity behind proxies.
- Validated task attachment URLs as HTTP(S) URLs only.

## Frontend Fixes

- Ensured the API client normalizes `VITE_API_URL` and appends `/api` exactly once.
- Improved network error messages.
- Updated submission downloads to fetch protected file endpoints with the JWT token.
- Added modal-local upload errors, upload loading state, and double-submit prevention.
- Updated upload accept filters to match the backend allowlist.
- Added admin UI actions for awarding points and badges.
- Added notification mark-read action in the main layout.
- Removed `/uploads` dev proxy because files are now protected behind the API.

## Deployment Documentation

- Updated `README.md`.
- Updated `outputs/render-deployment-guide.md` with:
  - backend and frontend Render settings,
  - required environment variables,
  - SQLite notes for free Render testing,
  - PostgreSQL recommendation for real production,
  - default owner warning,
  - protected upload policy,
  - static-site rewrite guidance,
  - troubleshooting notes.
- Added `render.yaml` support for backend/frontend deployment and SPA rewrites.

## Verification Results

- `python -m compileall backend/app backend/migrations backend/init_db.py`: passed.
- `cd frontend && npm install`: passed.
- `cd frontend && npm run build`: passed.
- Local backend checks:
  - `GET /health`: 200.
  - `GET /`: 200.
  - `HEAD /docs`: 200.
  - deployed frontend CORS preflight: 200 with `access-control-allow-origin`.
  - unauthenticated `GET /api/tasks`: 401.
- End-to-end local workflow:
  - owner login: passed.
  - create student: passed.
  - create task: passed.
  - student login: passed.
  - student uploads valid `proof.txt`: passed.
  - protected file download with owner student token: 200.
  - `.js` upload attempt: rejected with 400.
  - other student attempting to download private file: 404.

## Final Render Settings

Backend:

```text
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: sh start_render.sh
```

Backend environment:

```text
DATABASE_URL=sqlite:///./mawahib.db
PYTHON_VERSION=3.11.11
INITIAL_OWNER_EMAIL=owner@mawahib.com
INITIAL_OWNER_PASSWORD=ChangeMe123!
CORS_ORIGINS=["http://localhost:5173","http://localhost:8080","https://mawahib-platform-1.onrender.com"]
ALLOWED_HOSTS=localhost,127.0.0.1,mawahib-platform.onrender.com,mawahib-platform-1.onrender.com
```

Frontend:

```text
Root Directory: frontend
Build Command: npm install && npm run build
Publish Directory: dist
VITE_API_URL=https://mawahib-platform.onrender.com
Rewrite: /* -> /index.html
```

## Remaining Production Notes

- SQLite is acceptable only for free Render testing. Real production should use PostgreSQL with persistent storage and migrations.
- Local uploads on Render free instances are not durable. Real production should use persistent disk or object storage.
- Change `INITIAL_OWNER_PASSWORD` immediately after first deployment.
- Keep CORS and allowed hosts explicit; do not use wildcard values in production.
