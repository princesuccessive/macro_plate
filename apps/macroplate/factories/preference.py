import factory

from apps.macroplate.models import Preference


class PreferenceFactory(factory.DjangoModelFactory):
    """Factory for Preference model."""

    class Meta:
        model = Preference

    name = factory.LazyAttribute(lambda o: o.id.capitalize())

    @factory.lazy_attribute
    def id(self):
        return "-".join(factory.Faker('words').generate())
