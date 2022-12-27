from datetime import datetime
from decimal import Decimal
from functools import partial

from django.db.models import Count

from apps.core.constants import FINAL_LBS_COEFFICIENT, OUNCE_TO_POUND
from apps.macroplate.models import Meal, MealIngredient, PlanType
from apps.macroplate.services.export import (
    BaseTableExportService,
    ByDateExportServiceMixin,
)


class MealQuantityExportService(
    ByDateExportServiceMixin,
    BaseTableExportService,
):
    """Service to export meal quantity report."""
    columns = dict(
        meal='',
    )
    # columns which will be after plans
    columns_after = dict(
        total='Total #',
        lbs_ckd='Lbs Ckd',
        lbs_raw='Lbs Raw',
        lbs_final='Final (lbs)',
    )

    def __init__(self, date: datetime.date):
        """Initialize the service."""
        super().__init__(date)

        # add plan types to columns
        for plan in PlanType.objects.all():
            self.columns[plan.id] = plan.name
        self.columns.update(**self.columns_after)

    def rows_data(self) -> list:
        """Select Meals and add "count" to each meal.

        "count" - this is the number indicating how many times a given meal is
        assigned on that day.
        """
        return Meal.objects.filter(
            assignedmeal__assigned_menu__daily_menu__date=self.export_date,
        ).select_related(
            'plan_type'
        ).prefetch_related(
            'ingredients',
            'ingredients__ingredient',
        ).annotate(
            count=Count('assignedmeal'),
        )

    def process_data(self, rows_data):
        """Add total row to the end of table."""
        super().process_data(rows_data)

        self.data.append(self.empty_row.values())
        self.data.append(self._get_total_row().values())

    def after_process_data(self, rows_data):
        """Accumulate rows with the same name.

        The main idea of this method to sum all rows with equal name.
        We go along the rows, and sum them up if the rows have the same name
        """
        super().after_process_data(rows_data)

        grouped_rows = []
        names = {}

        for row in self.data:
            name = row[0]

            # if there is not row with current name yet in grouped rows
            if name not in names:
                grouped_rows.append(list(row))
                names[name] = len(grouped_rows) - 1
                continue

            # if there is a row with same name, add this row to exists
            current = grouped_rows[names[name]]
            for index in range(1, len(row)):
                v1, v2 = current[index], row[index]

                if v1 is None and v2 is None:
                    continue

                if 'count' in [v1, v2]:
                    # if some of numbers == 'count' then result = 'count'
                    current[index] = 'count'
                else:
                    # else sum this two numbers
                    current[index] = Decimal(v1 or 0) + Decimal(v2 or 0)
            grouped_rows[names[name]] = current

        # clear the data and set new grouped data
        self.data.wipe()
        self.data.headers = self.columns.values()
        self.data.extend(grouped_rows)

    def default_getter(self, meal: Meal, field: str):
        """This default getter used for get values for each Plan Type."""
        if meal.plan_type.id != field:
            return None

        return meal.count

    def get_meal(self, meal: Meal):
        """Get name of meal."""
        return meal.name

    def get_total(self, meal: Meal):
        """Get "Total" value, which equal to count of current meal."""
        return meal.count

    def get_lbs_ckd(self, meal: Meal):
        """Get "Lbs Ckd" value."""
        return self._get_lbs_for_meal(meal)

    def get_lbs_raw(self, meal: Meal):
        """Get "Lbs Raw" value."""
        return self._get_lbs_for_meal(meal, with_raw=True)

    def get_lbs_final(self, meal: Meal):
        """Get "Final lbs" value."""
        raw = self._get_lbs_for_meal(meal, with_raw=True)

        return raw * FINAL_LBS_COEFFICIENT if isinstance(raw, Decimal) else raw

    def _get_lbs_for_meal(self, meal: Meal, with_raw=False):
        """Get LBS value for current meal.

        If `with_raw` flag passed - conversion_raw will be used in calculations
        """
        # Don't use queryset filtering because items are prefetched
        protein_ingredients = [
            m for m in meal.ingredients.all() if m.is_protein
        ]
        if not protein_ingredients:
            return None

        # Don't use queryset filtering because items are prefetched
        count_ingredients = (m for m in meal.ingredients.all() if m.is_count)
        if any(count_ingredients):
            return 'count'

        # calculate sum of all lbs values
        get_value = partial(MealIngredient.get_lbs, with_raw=with_raw)
        value = sum(map(get_value, protein_ingredients))

        return value * OUNCE_TO_POUND

    def _get_total_row(self):
        """Generate total row, that contain sum of values in columns."""
        total_row = self.empty_row

        skip_cols = ['meal', 'lbs_ckd', 'lbs_raw', 'lbs_final']
        for col_index, col in enumerate(self.columns):
            if col in skip_cols:
                continue

            values = self.data.get_col(col_index)
            total_row[col] = sum(map(int, filter(None, values)))

        total_row['meal'] = 'Total'
        return total_row
