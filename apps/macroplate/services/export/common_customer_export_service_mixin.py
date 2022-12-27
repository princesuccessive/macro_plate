from collections import Counter
from datetime import datetime

from django.db.models import Prefetch

from apps.core.constants import DaysOfWeek
from apps.macroplate.models import Customer, DailySchedule


class CommonCustomerExportServiceMixin:
    """Mixin for export with customers."""
    export_date: datetime.date = None

    def __init__(self, *args, **kwargs):
        """Initialize the service."""
        self.locations_count = None

        super().__init__(*args, **kwargs)

    def rows_data(self):
        """Get customers information and remove customers without dishes."""
        qs = (
            Customer.objects
            .for_delivery(self.export_date)
            .select_related(
                'plan_type',
            )
            .prefetch_related(
                Prefetch(
                    'daily_schedules',
                    queryset=DailySchedule.objects.filter(
                        date=self.export_date,
                    ),
                    to_attr='current_daily_schedules',
                )
            )
            .has_dishes_for_date(self.export_date)
            .order_by(
                'plan_type',
                'first_name',
                'last_name',
            )
        )

        return qs

    def before_process_data(self, rows_data):
        """Prepare data for export.

        Before preparing, calculate users per each location (for 'ZIP' column)
        """
        locations = ((i.address, i.suite) for i in rows_data)
        self.locations_count = Counter(locations)

        super().before_process_data(rows_data)

    def get_plan_type(self, row_data: Customer):
        """Get plan name."""
        return row_data.plan_type.name

    @property
    def _today_is_monday(self):
        """Return true if today is Monday"""
        return self.export_date.weekday() == DaysOfWeek.MONDAY

    def _is_location_repeat(self, row_data: Customer):
        """If user has same location that other user, return true."""
        loc = (row_data.address, row_data.suite)
        return self.locations_count[loc] > 1

    def _current_daily_schedule(self, row_data: Customer):
        """Calculate count of bags for current user."""
        for schedule in row_data.current_daily_schedules:
            if schedule.date == self.export_date:
                return schedule
