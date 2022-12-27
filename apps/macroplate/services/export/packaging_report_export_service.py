from datetime import datetime

from apps.core.constants import WORKDAYS, DaysOfWeek
from apps.macroplate.models import Customer
from apps.macroplate.services.export import (
    BaseTableExportService,
    ByDateExportServiceMixin,
    CommonCustomerExportServiceMixin,
)


class PackagingReportExportService(
    ByDateExportServiceMixin,
    CommonCustomerExportServiceMixin,
    BaseTableExportService,
):
    """Service to export packaging report."""
    columns = dict(
        red='RED',
        zip='ZIP',
        full_name='Full Name',
        plan_string='Plan',
        monday='Mon',
        tuesday='Tuesday',
        wednesday='Wednesday',
        thursday='Thursday',
        friday='Friday',
        snacks_count='# of Snacks',
        snacks_notes='Snacks Notes',
        gluten_free='GF',
        nut_free='NF',
        welcome_note='WN',
        juice='Juice',
        coffee='Coffee',
        juice_dislikes='Juice dislikes',
        juice_requested='Juice requested',
    )

    def __init__(self, date: datetime.date):
        """Initialize the service."""
        super().__init__(date)
        self._remove_not_current_days_of_week()

    # Getters

    def get_red(self, row_data: Customer):
        """Get RED value for customer."""
        return 'RED' if row_data.red else None

    def get_zip(self, row_data: Customer):
        """If user has save location that other user show ZIP."""
        return 'ZIP' if self._is_location_repeat(row_data) else None

    def get_monday(self, row_data: Customer):
        return self._get_day_count(row_data, DaysOfWeek.MONDAY)

    def get_tuesday(self, row_data: Customer):
        return self._get_day_count(row_data, DaysOfWeek.TUESDAY)

    def get_wednesday(self, row_data: Customer):
        return self._get_day_count(row_data, DaysOfWeek.WEDNESDAY)

    def get_thursday(self, row_data: Customer):
        return self._get_day_count(row_data, DaysOfWeek.THURSDAY)

    def get_friday(self, row_data: Customer):
        return self._get_day_count(row_data, DaysOfWeek.FRIDAY)

    def get_gluten_free(self, row_data: Customer):
        """Get GF value for customer."""
        return 1 if row_data.gluten_free else None

    def get_juice(self, row_data: Customer):
        """Get JUICE value for customer."""
        return row_data.juice_count if self._today_is_monday else None

    def get_coffee(self, row_data: Customer):
        """Get COFFEE value for customer."""
        return row_data.coffee_count if self._today_is_monday else None

    def get_nut_free(self, row_data: Customer):
        """Get NF value for customer."""
        return 1 if row_data.nut_free else None

    def get_welcome_note(self, row_data: Customer):
        """Check that it's first delivery."""
        return 1 if row_data.first_delivery_date == self.export_date else None

    def _get_day_count(self, row_data: Customer, day_of_week: int) -> int:
        """Get count dishes in current day of week."""
        return self._current_daily_schedule(row_data).dishes_count

    def _remove_not_current_days_of_week(self):
        """Remove all days of week except current day.

        In "columns" we have all days of week, but in finally report wee need
        only one column with current day of week (for export date)
        """
        current_weekday = self.export_date.weekday()

        # create copy of dict to prevent changing the class variable
        columns_copy = self.columns.copy()
        for weekday in WORKDAYS:
            if weekday == current_weekday:
                continue
            key = DaysOfWeek.day_name(weekday).lower()
            del columns_copy[key]

        # set new columns
        self.columns = columns_copy

    @property
    def _today_is_monday(self):
        """Return true if today is Monday"""
        return self.export_date.weekday() == DaysOfWeek.MONDAY
