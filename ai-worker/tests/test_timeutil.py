from datetime import date, datetime, timezone

from app.timeutil import today_kst


def test_today_kst_uses_korean_calendar_date():
    assert today_kst(datetime(2026, 10, 7, 23, 30, tzinfo=timezone.utc)) == date(2026, 10, 8)
