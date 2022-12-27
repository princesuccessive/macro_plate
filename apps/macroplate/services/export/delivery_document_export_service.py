import math
from datetime import datetime

from apps.core.constants import DaysOfWeek
from apps.macroplate.models import Customer
from apps.macroplate.services.export import (
    BarcodeGenerationService,
    BaseTableExportService,
    ByDateExportServiceMixin,
    CommonCustomerExportServiceMixin,
)


class DeliveryDocumentExportService(
    ByDateExportServiceMixin,
    CommonCustomerExportServiceMixin,
    BaseTableExportService,
):
    """Service to export delivery information."""
    columns = dict(
        juice_coffee='J/C',
        full_name='Full Name',
        phone_number='Phone',
        address='Address',
        suite='Suite',
        city='City',
        state='State',
        zip='Zip',
        country='Country',
        plan_string='Plan',
        bags='Bags',
        lg='LG',
        bar_code='Bar Code',
        delivery_window='Delivery Window',
        delivery_notes='Notes',
    )
    default_country = 'USA'
    default_state = 'CA'

    def __init__(self, date: datetime.date):
        """Initialize the service."""
        super().__init__(date)
        self.barcode_generator = BarcodeGenerationService()

    # Getters

    def get_juice_coffee(self, row_data: Customer):
        """Get value of juice and coffee.

        It will be empty in all days except Monday
        """
        if not self._today_is_monday:
            return None

        juice = row_data.juice_count or 0
        coffee = row_data.coffee_count or 0

        return f'{juice}/{coffee}'

    def get_state(self, row_data: Customer):
        """Get state, it's fixed value."""
        return self.default_state

    def get_country(self, row_data: Customer):
        """Get country, it's fixed value."""
        return self.default_country

    def get_bags(self, row_data: Customer):
        """Calculate count of bags for current user."""
        schedule = self._current_daily_schedule(row_data)
        count_dishes = schedule.dishes_count
        return math.ceil(count_dishes / 4) if count_dishes else None

    def get_lg(self, row_data: Customer):
        """If user has save location that other user show ZIP."""
        return 'ZIP' if self._is_location_repeat(row_data) else None

    def get_bar_code(self, row_data: Customer):
        """Generate random barcode for each customer."""
        return self.barcode_generator.generate()

    @property
    def _today_is_monday(self):
        """Return true if today is Monday"""
        return self.export_date.weekday() == DaysOfWeek.MONDAY
