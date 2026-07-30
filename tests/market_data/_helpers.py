from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pytest


def require_zoneinfo(key: str) -> ZoneInfo:
    try:
        return ZoneInfo(key)
    except ZoneInfoNotFoundError:
        pytest.skip(f"time zone data is not installed for {key!r}")
