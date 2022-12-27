from typing import List, NamedTuple


class MealIngredientRow(NamedTuple):
    """Spec for the input csv-row for Meal Ingredient."""

    from_name: str
    quantity: str
    mod_type: str
    to_name: str
    flex: str


class IngredientRow(NamedTuple):
    """Spec for the input csv-row for Ingredient."""

    name: str
    quantity_type: str
    is_protein: str
    is_count: str
    conversion_raw: str
    preferences: List[str]


class MealRow(NamedTuple):
    """Spec for the input csv-row for Meal."""

    id: str
    name: str
    plan_type_id: str
    breakfast: str
    ingredients: List[MealIngredientRow]
