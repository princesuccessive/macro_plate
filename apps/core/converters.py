import datetime
from typing import Union

from django.utils import dateparse

from .utils import date_to_ymd


class DateConverter:
    """Converter to use 'date' in the url in YYYY-MM-DD format."""
    regex = r'([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))'

    def to_python(self, value: str) -> datetime.date:
        """Parse date from URL string."""
        return dateparse.parse_date(value)

    def to_url(self, value: Union[str, datetime.date]) -> str:
        """Convert `date` object to 'Y-m-d' string, return str as is."""
        if isinstance(value, datetime.date):
            return date_to_ymd(value)
        return value
