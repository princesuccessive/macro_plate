import factory
from factory import fuzzy

from apps.macroplate.models import MealModifier
from apps.macroplate.models.meal_modifiers import ModTypes

from .ingredient import IngredientFactory
from .meal import MealFactory


class MealModifierFactory(factory.DjangoModelFactory):
    """Factory for MealModifier model."""

    class Meta:
        model = MealModifier

    meal = factory.SubFactory(MealFactory)
    ingredient_from = factory.SubFactory(IngredientFactory)
    ingredient_to = factory.SubFactory(IngredientFactory)
    mod_type = fuzzy.FuzzyChoice([ModTypes.NO, ModTypes.SUB, ModTypes.EXTRA])
    is_soft = factory.Faker('boolean', chance_of_getting_true=50)
