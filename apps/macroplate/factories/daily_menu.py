import random

import factory

from apps.macroplate.models import DailyMenu, Meal
from apps.macroplate.models.daily_menu import DailyMenuItem


class DailyMenuFactory(factory.DjangoModelFactory):
    """Factory for DailyMenu model."""

    class Meta:
        model = DailyMenu

    date = factory.Faker(
        'date_between',
        start_date="-30d",
        end_date="+30d",
    )

    @factory.post_generation
    def meals(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if not extracted:
            # select or create 3 meals
            count_meals = random.randint(2, 5)
            count_in_db = Meal.objects.count()

            if count_in_db < count_meals:
                from apps.macroplate.factories import MealFactory
                MealFactory.create_batch(10)

            extracted = Meal.objects.all()[:count_meals]

        # A list of groups were passed in, use them
        order = 0
        for meal in extracted:
            DailyMenuItem.objects.create(
                daily_menu=self,
                meal=meal,
                order=order,
            )
            order += 1
