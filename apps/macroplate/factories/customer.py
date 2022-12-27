import random
from typing import List, Optional
from uuid import uuid4

import factory
from factory import fuzzy

from apps.core.constants import WORKDAYS
from apps.core.utils import get_week_start
from apps.macroplate.models import (
    Customer,
    DailySchedule,
    PlanType,
    Preference,
    create_history,
)

from .plan_type import PlanTypeFactory


@factory.django.mute_signals(create_history)
class CustomerFactory(factory.DjangoModelFactory):
    """Factory for Customer model."""

    class Meta:
        model = Customer

    external_id = factory.lazy_attribute(lambda x: uuid4())
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    phone_number = factory.Faker('phone_number')
    address = factory.Faker('address')
    suite = factory.Faker('building_number')
    city = factory.Faker('city')
    zip = factory.Faker('zipcode')
    delivery_notes = factory.Faker('catch_phrase')
    delivery_window = factory.Faker('catch_phrase')
    red = factory.Faker('boolean', chance_of_getting_true=33)
    plan_type = factory.SubFactory(PlanTypeFactory)
    snacks_count = fuzzy.FuzzyInteger(0, 4)
    snacks_notes = factory.Faker('catch_phrase')
    gluten_free = factory.Faker('boolean', chance_of_getting_true=30)
    nut_free = factory.Faker('boolean', chance_of_getting_true=30)
    juice_count = fuzzy.FuzzyInteger(4, 9)
    juice_requested = factory.Faker('catch_phrase')
    juice_dislikes = factory.Faker('catch_phrase')
    coffee_count = fuzzy.FuzzyInteger(0, 30)
    preferences_notes = factory.Faker('catch_phrase')
    meal_assignment_paused = False
    carbs = factory.Faker('catch_phrase')
    protein = factory.Faker('catch_phrase')
    fat = factory.Faker('catch_phrase')

    @factory.lazy_attribute
    def plan_type(self):
        try:
            return random.choice(PlanType.objects.all())
        except IndexError:
            return PlanTypeFactory()

    @factory.lazy_attribute
    def promo_code(self):
        """Generate random promo code"""
        return str(uuid4()).replace('-', '')[:10].upper()

    @factory.lazy_attribute
    def first_delivery_date(self):
        """Generate first delivery date"""
        first_delivery_date = factory.Faker(
            'date_between',
            start_date="-60d",
            end_date="-30d",
        ).generate()

        return get_week_start(first_delivery_date)

    @factory.post_generation
    def create_daily_schedules(
        self: Customer,
        create: bool,
        extracted: Optional[List[DailySchedule]],
        **kwargs,
    ):
        """Create default DailySchedule objects, or use provided."""
        if not create:
            return
        if not extracted:
            extracted = []
            for day_of_week in WORKDAYS:
                daily_schedule = DailySchedule(
                    customer=self,
                    date=None,
                    day_of_week=day_of_week,
                    has_delivery=True,
                    breakfasts=random.choice(range(3)),
                    lunches=random.choice(range(3)),
                )
                extracted.append(daily_schedule)
        DailySchedule.objects.bulk_create(extracted)


class CustomerWithPreferencesFactory(CustomerFactory):
    """Factory for Customer model with preferences."""

    @factory.post_generation
    def preferences(self, create, extracted, **kwargs):
        """Add Preferences to this Customer.

        If preferences not found - create this
        """
        if not create:
            return

        # if preferences not passed - create them
        if not extracted:
            count_preferences = random.randint(2, 5)
            count_in_db = Preference.objects.count()

            if count_in_db < count_preferences:
                from apps.macroplate.factories import PreferenceFactory
                PreferenceFactory.create_batch(10)

            extracted = Preference.objects.all()[:count_preferences]

        self.preferences.add(*extracted)
        self.save()
