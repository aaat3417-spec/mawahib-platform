#!/usr/bin/env sh
set -eu

case "${DATABASE_URL:-}" in
  sqlite*)
    python -m app.db.init_db
    ;;
  *)
    alembic upgrade head
    python -m app.db.init_db
    ;;
esac

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
