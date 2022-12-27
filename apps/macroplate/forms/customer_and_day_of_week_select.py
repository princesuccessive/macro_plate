from .customer_select import CustomerSelectForm
from .day_of_week_select import DayOfWeekSelectForm


class CustomerAndDayOfWeekSelectForm(CustomerSelectForm, DayOfWeekSelectForm):
    """Form for select customer and day of week."""
