"""Date utilities."""

from datetime import datetime, timezone


def now() -> str:
    """Get the current date and time in UTC.

    Returns
    -------
    str
        The current date and time in UTC.
    """
    return (
        datetime.now(tz=timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )
