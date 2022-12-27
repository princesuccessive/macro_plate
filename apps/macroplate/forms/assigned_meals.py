from django import forms

from apps.core.forms import CustomControlFormMixin
from apps.macroplate.models import AssignedMeal, AssignedMenu, Meal


class AssignedMealInlineForm(CustomControlFormMixin, forms.ModelForm):
    """Inline form for editing Assigned Meal."""

    class Meta:
        model = AssignedMeal
        fields = (
            'meal',
            'mods',
        )

    meal = forms.ModelChoiceField(
        required=False,
        queryset=Meal.objects.select_related('plan_type').all(),
        widget=forms.Select(attrs={
            'class': 'selectpicker',
            'data-live-search': 'true',
            'data-style': 'custom-select-picker',
        })
    )

    def __init__(self, meals_qs, *args, **kwargs):
        """Restrict choices for meal."""
        super().__init__(*args, **kwargs)
        self.fields['meal'].queryset = meals_qs


AssignedMealInlineFormSet = forms.inlineformset_factory(
    AssignedMenu,
    AssignedMeal,
    form=AssignedMealInlineForm,
    extra=1,
    can_delete=True,
)
