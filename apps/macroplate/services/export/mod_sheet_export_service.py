from datetime import datetime
from itertools import groupby
from operator import attrgetter

from apps.macroplate.models import AssignedMeal
from apps.macroplate.services.export import (
    BaseTableExportService,
    ByDateExportServiceMixin,
)


class ModSheetExportService(
    ByDateExportServiceMixin,
    BaseTableExportService,
):
    """Service to export Mod Sheet."""

    columns = dict(
        meal='',
        meal_type='Lunch/Dinner',
        plan='Plan',
        customer='Name',
        mods='Mod',
    )

    def __init__(self, date: datetime.date):
        """Initialize the service."""
        super().__init__(date)

    def rows_data(self):
        """Get customers information and remove customers without dishes."""
        assigned_meals = AssignedMeal.objects.filter(
            assigned_menu__daily_menu__date=self.export_date,
        ).exclude(
            mods=''
        ).select_related(
            'assigned_menu',
            'meal',
        ).prefetch_related(
            'assigned_menu__customer',
            'assigned_menu__customer__plan_type',
            'assigned_menu__daily_menu',
        ).order_by(
            'meal__breakfast',
            'meal__name',
            'assigned_menu__customer__plan_type__name',
            'assigned_menu__customer__first_name',
            'assigned_menu__customer__last_name',
        ).all()

        # Group rows by meal.
        rows = []
        for k, g in groupby(assigned_meals, key=attrgetter('meal')):
            rows.extend(list(g))
            # Add empty row between groups
            rows.append(None)

        return rows

    def get_meal(self, assigned_meal: AssignedMeal):
        """Get meal name."""
        return assigned_meal.meal.name

    def get_plan(self, assigned_meal: AssignedMeal):
        """Get plan name."""
        return assigned_meal.assigned_menu.customer.plan_string

    def get_meal_type(self, assigned_meal: AssignedMeal):
        """Get meal type."""
        return assigned_meal.get_meal_type_display()

    def get_customer(self, assigned_meal: AssignedMeal):
        """Get customer full name."""
        return assigned_meal.assigned_menu.customer.full_name

    def get_mods(self, assigned_meal: AssignedMeal):
        """Get meal mods."""
        return assigned_meal.mods
