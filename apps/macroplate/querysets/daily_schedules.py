import datetime

from django.db import models


class DailyScheduleQuerySet(models.QuerySet):
    """DailySchedule Query Set."""

    def get_custom_or_default(
        self,
        customer_id: int,
        schedule_date: datetime.date,
    ):
        """Get either custom schedule for date, or default for its week day."""
        date_query = (
            models.Q(date=schedule_date) |
            models.Q(
                date=None,
                day_of_week=schedule_date.weekday(),
            )
        )
        return self.filter(
            date_query,
            customer_id=customer_id,
        ).order_by('date')

    def order_by_weekday(self):
        """Order by day of week."""
        return self.order_by('day_of_week')

    def only_default(self):
        """Exclude schedules, which have custom-set dates."""
        return self.exclude(date__isnull=False)
