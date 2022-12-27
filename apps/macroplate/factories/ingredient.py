import factory

from apps.core.constants import QuantityType
from apps.macroplate.models import Ingredient


class IngredientFactory(factory.DjangoModelFactory):
    """Factory for Ingredient model."""

    class Meta:
        model = Ingredient

    name = factory.Faker('sentence', nb_words=2)
    is_protein = factory.Faker('boolean', chance_of_getting_true=33)
    count = factory.Faker('boolean', chance_of_getting_true=33)

    @factory.lazy_attribute
    def quantity_type(self):
        if self.is_protein and self.count:
            return QuantityType.COUNT
        return QuantityType.OUNCE
