from typing import List

from django.db.models import Count, Max

from apps.core.utils import yes_or_none
from apps.macroplate.models import Ingredient

from .base_table_export_service import BaseTableExportService


class AllIngredientsExportService(BaseTableExportService):
    """Service to export all Ingredients.

    Exported file has next columns:
        - Name
        - Quantity Type
        - Protein
        - Countable
        - Conversion Raw
        - Preference (1)
        - Preference (2)
        - ...
        - Preference (N)

    Preference column repeats N times, where N - it is max count of preferences
    """

    report_progress = False

    # Max count of preferences
    pref_count = 0
    # Column names for preferences
    pref_columns = []

    def __init__(self):
        """Dynamically create columns for preferences."""
        super().__init__()

        # calculate count preferences for each ingredient, and create columns
        result = Ingredient.objects.annotate(
            count_preferences=Count('preferences'),
        ).aggregate(
            max_preferences=Max('count_preferences')
        )

        self.pref_count = result.get('max_preferences', 0)
        self.pref_columns = [
            f'pref_{num}' for num in range(1, self.pref_count + 1)
        ]

        self.columns = dict(
            name='Name',
            quantity_type='Quantity Type',
            is_protein='Protein',
            count='Countable',
            conversion_raw='Conversion Raw',
        )

        pairs = zip(self.pref_columns, range(1, self.pref_count + 1))
        self.columns.update({
            name: f'Preference ({num})' for name, num in pairs
        })

    def rows_data(self) -> List[dict]:
        """Get all ingredients with preferences in dict format."""
        rows = []
        ingredients = Ingredient.objects.prefetch_related('preferences')
        for ingredient in ingredients:
            row = dict(
                name=ingredient.name,
                quantity_type=ingredient.quantity_type,
                is_protein=yes_or_none(ingredient.is_protein),
                count=yes_or_none(ingredient.count),
                conversion_raw=ingredient.conversion_raw,
            )
            pref_names = list(
                pref.name for pref in ingredient.preferences.all()
            )
            row.update(zip(self.pref_columns, pref_names))
            rows.append(row)

        return rows

    @staticmethod
    def default_getter(row_data: dict, field: str):
        """Be default, get item from the dict."""
        value = row_data.get(field, None)

        if not value or value == '0':
            return None
        return value
