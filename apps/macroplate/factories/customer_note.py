import factory

from apps.macroplate.models import CustomerNote

from . import CustomerFactory


class CustomerNoteFactory(factory.DjangoModelFactory):
    """Factory for CustomerNote model."""

    class Meta:
        model = CustomerNote

    customer = factory.SubFactory(CustomerFactory)
    title = factory.Faker('catch_phrase')
    text = factory.Faker('catch_phrase')
    date = factory.Faker(
        'date_between',
        start_date="-30d",
        end_date="-1d",
    )
