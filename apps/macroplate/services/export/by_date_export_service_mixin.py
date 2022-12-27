from datetime import datetime

from apps.core.constants import WORKDAYS


class ByDateExportServiceMixin:
    """Mixin for export by date."""

    def __init__(self, date: datetime.date, *args, **kwargs):
        """Initialize the service."""
        if date.weekday() not in WORKDAYS:
            raise ValueError('Date must be workday')

        self.export_date = date

        super().__init__(*args, **kwargs)
