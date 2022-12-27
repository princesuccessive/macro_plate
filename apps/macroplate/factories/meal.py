import factory

from apps.macroplate.models import Meal

from .ingredient import IngredientFactory
from .plan_type import PlanTypeFactory


class MealFactory(factory.DjangoModelFactory):
    """Factory for Meal model."""

    class Meta:
        model = Meal

    name = factory.Faker('sentence', nb_words=2)
    breakfast = factory.Faker('boolean', chance_of_getting_true=33)
    plan_type = factory.SubFactory(PlanTypeFactory)
    prep_instructions = factory.Faker('catch_phrase')

    @factory.post_generation
    def preferences(self, create, extracted, **kwargs):
        """Add Ingredient with preference to this Meal."""
        if not create:
            return

        from .meal_ingredient import MealIngredientFactory

        if not extracted:
            return

        for preference in extracted:
            ingredient = IngredientFactory()
            ingredient.preferences.add(preference)
            MealIngredientFactory(
                meal=self,
                ingredient=ingredient,
            )
