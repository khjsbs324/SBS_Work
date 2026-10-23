from datetime import date, timedelta


def next_weekday(unit_end_date):
    value = date.fromisoformat(unit_end_date) + timedelta(days=1)
    while value.weekday() >= 5:
        value += timedelta(days=1)
    return value.isoformat()
