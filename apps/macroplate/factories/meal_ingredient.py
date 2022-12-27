import factory
from factory import fuzzy

from apps.macroplate.models import MealIngredient

from .ingredient import IngredientFactory
from .meal import MealFactory


class MealIngredientFactory(factory.DjangoModelFactory):
    """Factory for MealIngredient model."""

    class Meta:
        model = MealIngredient

    meal = factory.SubFactory(MealFactory)
    ingredient = factory.SubFactory(IngredientFactory)
    quantity = fuzzy.FuzzyFloat(low=1)
