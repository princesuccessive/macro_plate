from typing import List

from django.db.models import Count, Max

from apps.core.utils import yes_or_none
from apps.macroplate.models import Meal, MealModifier

from .base_table_export_service import BaseTableExportService


class AllMealsExportService(BaseTableExportService):
    """Service to export Meals.

    Exported file has next columns:
        - ID
        - Name
        - Plan Type ID
        - Breakfast
        - Ingredient (1)
        - Quantity (1)
        - Mod Type (1)
        - Ingredient to (1)
        - Flex (1)
        - ...
        - Ingredient (N)
        - Quantity (N)
        - Mod Type (N)
        - Ingredient to (N)
        - Flex (N)

    Last 5 column repeats N times, where N - it is max count of ingredients.
    """

    report_progress = False

    ingredients_count = 0
    ingredients_columns = None

    def __init__(self):
        """Dynamically create columns for ingredients.

        For each modifier we create 5 columns:
        - Ingredient
        - Quantity
        - Mod Type
        - Ingredient to
        - Flex
        """
        super().__init__()

        # calculate count ingredients for each meal, and create columns
        result = Meal.objects.annotate(
            count_ingredients=Count('ingredients'),
        ).aggregate(
            max_ingredients=Max('count_ingredients')
        )

        self.columns = dict(
            id='ID',
            name='Name',
            plan_type_id='Plan Type ID',
            breakfast='Breakfast',
        )

        self.ingredients_count = result.get('max_ingredients', 0)
        self.ingredients_columns = []
        for num in range(1, self.ingredients_count + 1):
            cols = [
                f'ingredient_{num}',
                f'quantity_{num}',
                f'mod_type_{num}',
                f'ingredient_to_{num}',
                f'flex_{num}',
            ]
            cols_names = [
                f'Ingredient ({num})',
                f'Quantity ({num})',
                f'Modifier Type ({num})',
                f'Ingredient To ({num})',
                f'Flex ({num})',
            ]
            self.ingredients_columns.extend(cols)
            self.columns.update(zip(cols, cols_names))

    def rows_data(self) -> List[dict]:
        """Get all meals with modifiers."""
        rows = []
        meals = Meal.objects.prefetch_related(
            'plan_type',
            'mods',
            'mods__ingredient_from',
            'mods__ingredient_to',
            'ingredients',
            'ingredients__ingredient',
        )
        for meal in meals.all():
            row = dict(
                id=meal.id,
                name=meal.name,
                plan_type_id=meal.plan_type_id,
                breakfast=yes_or_none(meal.breakfast),
            )

            mods_map = {mod.ingredient_from: mod for mod in meal.mods.all()}

            for num, meal_ingredient in enumerate(meal.ingredients.all(), 1):
                ingredient = meal_ingredient.ingredient
                row.update(**{
                    f'ingredient_{num}': meal_ingredient.ingredient.name,
                    f'quantity_{num}': meal_ingredient.quantity or 0,
                })
                mod: MealModifier = mods_map.get(ingredient, None)
                if not mod:
                    continue

                ingredient_to_name = ''
                if mod.ingredient_to:
                    ingredient_to_name = mod.ingredient_to.name

                row.update(**{
                    f'mod_type_{num}': mod.get_mod_type_display(),
                    f'ingredient_to_{num}': ingredient_to_name,
                    f'flex_{num}': yes_or_none(mod.is_soft),
                })
            rows.append(row)
        return rows

    @staticmethod
    def default_getter(row_data: dict, field: str):
        """Be default, get item from the dict."""
        value = row_data.get(field, None)

        if not value or value == '0':
            return None
        return value
