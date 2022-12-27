from django import forms
from django.forms.formsets import ORDERING_FIELD_NAME

from apps.core.forms import CustomControlFormMixin
from apps.macroplate.models import Meal


class SelectMealForm(CustomControlFormMixin, forms.Form):
    """MealsIngredient edition form."""

    meal = forms.ModelChoiceField(
        required=False,
        queryset=Meal.objects.select_related('plan_type').all(),
        widget=forms.Select(attrs={
            'class': 'selectpicker',
            'data-live-search': 'true',
            'data-style': 'custom-select-picker',
        })
    )


class BaseSelectMealFormSet(forms.BaseFormSet):
    def clean(self):
        """Validate that all meals specified and meals don't have duplicates"""
        super().clean()

        if any(self.errors):
            return

        meals = set()
        for form in self.forms:
            meal = form.cleaned_data.get('meal')
            if form.cleaned_data.get('DELETE'):
                form.errors.clear()
                continue

            if any(self.errors) or not meal:
                continue

            if meal in meals:
                # meal is unique in menu
                form.add_error('meal', 'This meal has already been chosen.')
            else:
                meals.add(meal)

    def add_fields(self, form, index):
        """Hide ORDER field."""
        super().add_fields(form, index)

        if self.can_order:
            form.fields[ORDERING_FIELD_NAME].widget = forms.HiddenInput()


SelectMealFormSet = forms.formset_factory(
    form=SelectMealForm,
    formset=BaseSelectMealFormSet,
    can_delete=True,
    can_order=True,
    extra=0,
)
