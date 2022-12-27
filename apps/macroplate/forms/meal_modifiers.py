from django import forms
from django.forms import BaseInlineFormSet

from apps.core.forms import CustomControlFormMixin
from apps.macroplate.models import Meal, MealModifier


class MealModifierInlineForm(CustomControlFormMixin, forms.ModelForm):
    """Meal Modifier edition form."""

    class Meta:
        model = MealModifier
        fields = [
            'ingredient_from',
            'mod_type',
            'ingredient_to',
            'is_soft',
        ]


class MealModifierFormSet(BaseInlineFormSet):

    def clean(self):
        """Ingredients in field `ingredient_from` don't repeats."""
        ingredient_ids = set()
        for form in self.forms:
            from_id = form.instance.ingredient_from_id
            to_id = form.instance.ingredient_to_id

            if not from_id and not to_id:
                continue

            if from_id in ingredient_ids:
                form.add_error('ingredient_from', 'Mod already exists')
            ingredient_ids.add(form.instance.ingredient_from_id)


def create_meal_modifier_formset(extra=1):
    """Create FormSet with extra params."""

    return forms.inlineformset_factory(
        Meal,
        MealModifier,
        formset=MealModifierFormSet,
        form=MealModifierInlineForm,
        can_delete=True,
        extra=extra,
    )
