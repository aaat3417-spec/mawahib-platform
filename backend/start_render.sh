#!/usr/bin/env sh
set -eu

python -m app.db.init_db
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
