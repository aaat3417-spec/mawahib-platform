#!/usr/bin/env sh
set -eu

BACKUP_DIR="${BACKUP_DIR:-backups}"
POSTGRES_DB="${POSTGRES_DB:-mawahib}"
POSTGRES_USER="${POSTGRES_USER:-mawahib}"
STAMP="$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR"

docker compose exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$BACKUP_DIR/mawahib_${STAMP}.sql"
tar -czf "$BACKUP_DIR/uploads_${STAMP}.tar.gz" uploads

printf 'Created %s and %s\n' "$BACKUP_DIR/mawahib_${STAMP}.sql" "$BACKUP_DIR/uploads_${STAMP}.tar.gz"

