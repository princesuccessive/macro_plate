import re
from datetime import datetime, timedelta
from typing import Iterator, Optional

from django.utils import dateformat, timezone
from django.utils.formats import date_format as df

from apps.core.constants import WORKDAYS, DaysOfWeek


def date_to_ymd(date: datetime.date) -> str:
    """Format date to a `Y-m-d` string."""
    return dateformat.format(date, "Y-m-d")


def get_weeks_choices() -> list:
    """Generate choices for week select."""
    now = timezone.now().date()
    current_week_start = get_week_start(now)
    current_week_end = current_week_start + timedelta(days=6)

    next_week_start = current_week_start + timedelta(days=7)
    next_week_end = next_week_start + timedelta(days=6)

    current_label = f'{df(current_week_start)} - {df(current_week_end)}'
    next_label = f'{df(next_week_start)} - {df(next_week_end)}'

    return [
        (current_week_start, f'Current week ({current_label})'),
        (current_week_start + timedelta(days=7), f'Next week ({next_label})'),
    ]


def get_nearest_work_day(date: datetime.date) -> datetime.date:
    """Get nearest work day.

    If "date" is saturday or sunday - it's return next monday date.
    Else return "date" value
    """
    if date.weekday() in [DaysOfWeek.SATURDAY, DaysOfWeek.SUNDAY]:
        return date - timedelta(days=date.weekday()) + timedelta(days=7)
    return date


def get_days_choices() -> list:
    """Generate choices for day select.

    We don't show weekends, that's why if the next day is Saturday - we move
    the pointer forward to Monday.
    """
    current_day = timezone.now().date()

    nearest_work_day = get_nearest_work_day(current_day)
    if nearest_work_day != current_day:
        return [(nearest_work_day, f'Next day ({nearest_work_day})')]

    next_day = current_day + timedelta(days=1)
    if next_day.weekday() == DaysOfWeek.SATURDAY:
        # If next day is weekend, move next day to monday
        next_day = current_day + timedelta(days=3)

    return [
        (current_day, f'Current day ({current_day})'),
        (next_day, f'Next day ({next_day})'),
    ]


def get_week_start(date: datetime.date) -> datetime.date:
    """Get the start date of the current week."""
    return date - timedelta(days=date.weekday())


def get_week_end(date: datetime.date) -> datetime.date:
    """Get the end date of the current week."""
    return get_week_start(date) + timedelta(days=6)


def clear_string(string):
    """Remove from string all except numbers, letters and spaces."""
    return (re.sub(r'[^\w ]', '', string) or '').strip().lower()


def date_range(
    date_from: datetime.date,
    date_to: datetime.date,
    workdays_only: bool = False
) -> Iterator:
    """Return a generator for date range [date_from, date_to].

    If argument workdays = True, it will yields only workdays.

    Arguments:
        date_from: start date
        date_to: end date
        workdays_only: return only workdays
    """
    current_date = date_from
    delta = timedelta(days=1)
    while current_date <= date_to:
        if not workdays_only or current_date.weekday() in WORKDAYS:
            yield current_date
        current_date += delta


def yes_or_none(value: bool) -> Optional[str]:
    """Convert bool value to 'Yes' or None."""
    return 'Yes' if value else None


def is_yes(value: Optional[str]) -> bool:
    """Check that current value equal to 'Yes'."""
    return value == 'Yes'


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
