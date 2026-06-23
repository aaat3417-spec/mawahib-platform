from datetime import UTC, date, datetime, time


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_today() -> date:
    return utc_now().date()


def utc_day_start(day: date) -> datetime:
    return datetime.combine(day, time.min, tzinfo=UTC)

