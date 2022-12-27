from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.macroplate.factories import MealModifierFactory
from apps.macroplate.models import MealModifier


class TestMealModifier(TestCase):
    """Test for the `MealModifier` model."""

    def test_sub_extra_modifier_without_ingredient_to(self):
        """Ensure error is raised for SUB/EXTRA mods without ingredient_to."""
        for mod_type in (1, 2):
            meal_modifier: MealModifier = MealModifierFactory(
                mod_type=mod_type,
            )
            meal_modifier.clean()
            meal_modifier.ingredient_to = None
            expected_msg = (
                'For SUB/EXTRA type the second ingredient must be not empty'
            )
            with self.assertRaisesRegex(ValidationError, expected_msg):
                meal_modifier.clean()

    def test_no_modifier_with_ingredient_to(self):
        """Ensure error is raised for NO mods with `ingredient_to`."""
        meal_modifier: MealModifier = MealModifierFactory(mod_type=0)
        expected_msg = 'For NO type the second ingredient must be empty'

        with self.assertRaisesRegex(ValidationError, expected_msg):
            meal_modifier.clean()

        meal_modifier.ingredient_to = None
        meal_modifier.clean()
