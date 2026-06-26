#!/usr/bin/env python3
"""Export database tables to a JSON file without modifying the database."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from sqlalchemy import inspect, select  # noqa: E402

from app.db.base import Base  # noqa: E402,F401
from app.db.session import SessionLocal, engine  # noqa: E402


def serialize(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def export_database(output: Path) -> None:
    inspector = inspect(engine)
    payload = {}
    with SessionLocal() as db:
        for table_name in inspector.get_table_names():
            table = Base.metadata.tables.get(table_name)
            if table is None:
                continue
            rows = db.execute(select(table)).mappings().all()
            payload[table_name] = [
                {key: serialize(value) for key, value in row.items()}
                for row in rows
            ]

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Exported {len(payload)} tables to {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Mawahib database tables to JSON.")
    parser.add_argument("--output", default="backups/mawahib_export.json", help="Output JSON path.")
    args = parser.parse_args()
    export_database(Path(args.output))


if __name__ == "__main__":
    main()
