from django.test import TestCase

from apps.macroplate.factories import (
    CustomerFactory,
    MealFactory,
    MealModifierFactory,
    PlanTypeFactory,
    PreferenceFactory,
)
from apps.macroplate.services.assigned_menu_service import (
    check_meal_match_to_customer,
    get_available_meals_for_customer,
)


class TestAssignedMenuServiceCheckMatching(TestCase):
    """Test for `check_meal_match_to_customer`."""

    def setUp(self):
        self.preference = PreferenceFactory()
        plan_type = PlanTypeFactory()

        # Create the customer with preference
        self.customer_with_pref = CustomerFactory(plan_type=plan_type)
        self.customer_with_pref.preferences.add(self.preference)

        # Create the customer with other preference
        self.customer_with_other_pref = CustomerFactory(plan_type=plan_type)
        self.customer_with_other_pref.preferences.add(PreferenceFactory())

        # create the meal with current preference
        self.meal = MealFactory(
            plan_type=plan_type,
            preferences=[self.preference],
        )

    def test_matching_with_preferences_when_mod_not_exists(self):
        """Case, when meal contains ingredient that customers don't like, and
        mod for this ingredient doesn't exists.

        If there are ingredients in a meal that the customer doesn't like, and
        meals doesn't have mods for this ingredient, that meal shouldn't be
        matched.
        """
        matched, _ = check_meal_match_to_customer(
            customer=self.customer_with_pref,
            meal=self.meal,
        )
        self.assertFalse(matched)

    def test_matching_with_other_preferences(self):
        """Case, when meal contains ingredient that customers indifferent."""
        matched, _ = check_meal_match_to_customer(
            customer=self.customer_with_other_pref,
            meal=self.meal,
        )
        self.assertTrue(matched)

    def test_matching_when_mod_exists(self):
        """Case, when meal contains ingredient that customers don't like,
        and has a modifier for this ingredient.

        If there are ingredients in a meal that the customer does not like, and
        the meal has the modifier for this ingredient, then the meal should
        be matched with modifiers.
        """
        modifier = MealModifierFactory(
            meal=self.meal,
            ingredient_from=self.meal.ingredients.first().ingredient
        )
        matched, mods = check_meal_match_to_customer(
            customer=self.customer_with_pref,
            meal=self.meal,
        )
        self.assertTrue(matched)
        self.assertEqual({modifier}, mods)
        modifier.delete()


class TestAssignedMenuServiceGetAvailableMealsForCustomer(TestCase):
    """Test for `get_available_meals_for_customer`."""

    def setUp(self):
        plan_type = PlanTypeFactory()

        # create the meal with current preference
        self.meal = MealFactory(
            plan_type=plan_type,
        )
        self.another_meal = MealFactory(
            plan_type=plan_type,
        )
        self.meal_to_be_preferred = MealFactory(
            plan_type=plan_type,
        )

        # create the customer with excluded meal
        self.customer_with_excluded_meal = CustomerFactory(plan_type=plan_type)
        self.customer_with_excluded_meal.excluded_meals.add(
            self.meal
        )

    def test_matching_with_exclude(self):
        """Case, when customer exclude some meal, and we try to assign it."""

        meals = get_available_meals_for_customer(
            customer=self.customer_with_excluded_meal,
            meals=[self.meal, self.another_meal],
        )
        self.assertIn(self.another_meal, meals)
        self.assertNotIn(self.meal, meals)

    def test_preferred_meal_prioritized(self):
        """Ensure meal is first in list after it was prioritized."""
        get_meals_kwargs = {
            'customer': self.customer_with_excluded_meal,
            'meals': [self.another_meal, self.meal_to_be_preferred],
        }
        meals = get_available_meals_for_customer(**get_meals_kwargs)
        self.assertIs(meals[0], self.another_meal)

        self.customer_with_excluded_meal.preferred_meals.add(
            self.meal_to_be_preferred,
        )
        meals = get_available_meals_for_customer(**get_meals_kwargs)
        self.assertIs(meals[0], self.meal_to_be_preferred)
