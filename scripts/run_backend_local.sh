#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p work uploads/submissions uploads/profile_images uploads/certificates uploads/projects
LOCAL_DB_PATH="$ROOT_DIR/work/mawahib-local.db"

PYTHON_BIN="${PYTHON_BIN:-}"
if [ -z "$PYTHON_BIN" ]; then
  for candidate in python3.12 python3.11 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
      PYTHON_BIN="$candidate"
      break
    fi
  done
fi

if [ -z "$PYTHON_BIN" ]; then
  echo "Python 3.11+ is required, but no python3 command was found."
  exit 1
fi

"$PYTHON_BIN" - <<'PY'
import sys

if sys.version_info < (3, 11):
    version = ".".join(str(part) for part in sys.version_info[:3])
    raise SystemExit(f"Python 3.11+ is required. Found Python {version}.")
PY

if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi

source .venv/bin/activate
export PIP_DISABLE_PIP_VERSION_CHECK=1
python -m pip install -r backend/requirements.txt

export DATABASE_URL="${DATABASE_URL:-sqlite:///$LOCAL_DB_PATH}"
export AUTO_CREATE_TABLES="${AUTO_CREATE_TABLES:-true}"
export SECRET_KEY="${SECRET_KEY:-local-development-secret-key-change-before-production}"
export CORS_ORIGINS="${CORS_ORIGINS:-http://localhost:5173,http://127.0.0.1:5173}"
export ALLOWED_HOSTS="${ALLOWED_HOSTS:-localhost,127.0.0.1,0.0.0.0}"
export DOCS_ENABLED="${DOCS_ENABLED:-true}"
export INITIAL_OWNER_EMAIL="${INITIAL_OWNER_EMAIL:-owner@mawahib.local}"
export INITIAL_OWNER_PASSWORD="${INITIAL_OWNER_PASSWORD:-ChangeMe123!}"
export INITIAL_OWNER_NAME="${INITIAL_OWNER_NAME:-Mawahib Owner}"

cd backend
UVICORN_ARGS=(app.main:app --host 0.0.0.0 --port 8000)
if [ "${RELOAD:-false}" = "true" ]; then
  UVICORN_ARGS+=(--reload)
fi

exec uvicorn "${UVICORN_ARGS[@]}"
