class PreferenceNotFoundExceptions(Exception):
    """Preference not found."""


class IngredientNotFoundException(Exception):
    """Ingredient not found."""


class PlanTypeNotFoundException(Exception):
    """PlanType not found."""


class DuplicatedIngredientException(Exception):
    """Try to add duplicated ingredient into meal."""


class InvalidIngredientQuantityException(Exception):
    """Try to add ingredient with 0 or negative quantity."""


class DuplicatedMealException(Exception):
    """Try to add duplicated meal."""


class InvalidDataException(Exception):
    """Invalid data error."""
