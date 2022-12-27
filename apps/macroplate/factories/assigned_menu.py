import random

import factory

from apps.macroplate.factories import CustomerFactory, DailyMenuFactory
from apps.macroplate.models import AssignedMeal, AssignedMenu


class AssignedMenuFactory(factory.DjangoModelFactory):
    """Factory for AssignedMenu model."""

    class Meta:
        model = AssignedMenu

    customer = factory.SubFactory(CustomerFactory)
    daily_menu = factory.SubFactory(DailyMenuFactory)


class AssignedMenuWithMealsFactory(AssignedMenuFactory):
    """Factory for AssignedMenu model."""

    class Meta:
        model = AssignedMenu

    customer = factory.SubFactory(CustomerFactory)
    daily_menu = factory.SubFactory(DailyMenuFactory)

    @factory.post_generation
    def assigned_meals(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if not extracted:
            extracted = [random.choice(self.daily_menu.meals.all())]

        # A list of groups were passed in, use them
        for meal in extracted:
            AssignedMeal.objects.create(
                meal=meal,
                mods='',
                assigned_menu=self,
            )
