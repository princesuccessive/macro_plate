from django import forms

from apps.core.forms import CustomControlFormMixin
from apps.macroplate.models import Meal, MealIngredient


class MealIngredientInlineForm(CustomControlFormMixin, forms.ModelForm):
    """MealsIngredient edition form."""

    class Meta:
        model = MealIngredient
        fields = '__all__'

    def clean_quantity(self):
        """Quantity should be greater then 0."""
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise forms.ValidationError("Quantity should be greater then 0")
        return quantity


def create_meal_ingredient_formset(extra=1):
    """Create FormSet with extra params."""

    return forms.inlineformset_factory(
        Meal,
        MealIngredient,
        form=MealIngredientInlineForm,
        fields=['ingredient', 'quantity'],
        can_delete=True,
        extra=extra,
    )
