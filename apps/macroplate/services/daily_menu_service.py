import datetime

from apps.macroplate.models import DailyMenu
from apps.macroplate.models.daily_menu import DailyMenuItem


class DailyMenuService(object):
    """Service for working with user schedules."""

    @staticmethod
    def copy_from_date_to_date(
        from_date: datetime.date,
        to_date: datetime.date,
    ):
        """Copy menu from one date to another date."""
        menu_to, _ = DailyMenu.objects.get_or_create(date=to_date)
        menu_to.meals.clear()

        menu_from = DailyMenu.objects.get(date=from_date)
        from_items = DailyMenuItem.objects.filter(daily_menu=menu_from)

        for item in from_items:
            DailyMenuItem.objects.create(
                daily_menu=menu_to,
                meal=item.meal,
                order=item.order,
            )
