from datetime import datetime, timezone


def to_datetime(datetime_str: str|None) -> datetime|None:
    if str is None:
        return None
    return datetime.fromisoformat(datetime_str).replace(tzinfo=timezone.utc)


def get_now() -> datetime:
    return datetime.now(timezone.utc)
