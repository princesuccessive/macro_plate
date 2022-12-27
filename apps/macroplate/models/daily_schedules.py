from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.constants import DaysOfWeek
from apps.macroplate.querysets import DailyScheduleQuerySet


class DailySchedule(models.Model):
    """Model for Daily Schedule.

    Contains information about the schedule for a specific day of week.
    """
    customer = models.ForeignKey(
        to='Customer',
        on_delete=models.CASCADE,
        related_name='daily_schedules',
        verbose_name=_('Customer'),
    )
    day_of_week = models.PositiveIntegerField(
        choices=DaysOfWeek.CHOICES,
        verbose_name=_('Day of week'),
    )
    date = models.DateField(
        null=True,
        verbose_name=_('Date'),
    )
    has_delivery = models.BooleanField(
        default=True,
        verbose_name=_('Has delivery?'),
        help_text=_('Is delivery made on this date or not.'),
    )
    breakfasts = models.PositiveIntegerField(
        verbose_name=_('Breakfasts'),
    )
    lunches = models.PositiveIntegerField(
        verbose_name=_('Lunches'),
    )

    objects = DailyScheduleQuerySet.as_manager()

    class Meta:
        verbose_name = _('Daily schedule')
        verbose_name_plural = _('Daily schedules')
        unique_together = (
            ('customer', 'day_of_week', 'date'),
        )

    def __str__(self):
        """Return string representation, adjusted for custom or default."""
        message = f'Daily schedule for {self.customer} for {self.day_name}'

        if self.is_default:
            return f'Default {message}'
        return f'{message} ({self.date})'

    @property
    def is_default(self):
        """Return true if it's default schedule."""
        return self.date is None

    @property
    def day_name(self):
        """Return human day of week."""
        return DaysOfWeek.day_name(self.day_of_week)

    @property
    def dishes_count(self):
        """Return count of all dishes in this day."""
        return self.breakfasts + self.lunches
