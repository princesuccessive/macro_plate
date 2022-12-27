import factory

from apps.macroplate.models import PlanType


class PlanTypeFactory(factory.DjangoModelFactory):
    """Factory for PlanType model."""

    class Meta:
        model = PlanType

    name = factory.LazyAttribute(lambda o: o.id.capitalize())

    @factory.lazy_attribute
    def id(self):
        return "-".join(factory.Faker('words').generate())
