from django import forms

from apps.core.constants import DaysOfWeek
from apps.core.forms import LimitEditableFieldsFormMixin

from ..models import Customer, Meal, Preference
from ..models.customers import PlanPriority

multiple_select_widget = forms.SelectMultiple(attrs={
    'class': 'selectpicker',
    'data-live-search': 'true',
    'data-style': 'custom-select-picker',
    'multiple': True,
    'data-actions-box': 'true',
})


class CustomerForm(LimitEditableFieldsFormMixin, forms.ModelForm):
    """Customer edition form."""

    class Meta:
        model = Customer
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'address',
            'suite',
            'city',
            'zip',
            'first_delivery_date',
            'delivery_notes',
            'delivery_window',
            'red',
            'plan_type',
            'plan_priority',
            'snacks_count',
            'snacks_notes',
            'gluten_free',
            'nut_free',
            'juice_count',
            'juice_requested',
            'juice_dislikes',
            'coffee_count',
            'preferences',
            'preferences_notes',
            'promo_code',
            'meal_assignment_paused',
            'excluded_meals',
            'preferred_meals',
            'carbs',
            'protein',
            'fat',
        ]
        widgets = {
            'first_delivery_date': forms.TextInput(
                attrs={'type': 'date'}
            )
        }
        editable_fields = [
            'red',
            'snacks_notes',
            'gluten_free',
            'nut_free',
            'juice_dislikes',
            'juice_requested',
            'preferences',
            'preferences_notes',
            'excluded_meals',
            'preferred_meals',
            'carbs',
            'protein',
            'fat',
        ]

    plan_priority = forms.ChoiceField(
        choices=PlanPriority.CHOICES,
        widget=forms.RadioSelect
    )
    preferences = forms.ModelMultipleChoiceField(
        queryset=Preference.objects.all(),
        required=False,
        widget=multiple_select_widget,
    )
    excluded_meals = forms.ModelMultipleChoiceField(
        queryset=Meal.objects.all(),
        required=False,
        widget=multiple_select_widget,
    )
    preferred_meals = forms.ModelMultipleChoiceField(
        queryset=Meal.objects.all(),
        required=False,
        widget=multiple_select_widget,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.edit:
            return

        # load list of all meals and select meals for selected plan type
        meals = self.fields['excluded_meals'].queryset
        filtered = meals.filter(plan_type_id=self.instance.plan_type_id)
        self.fields['excluded_meals'].queryset = filtered
        self.fields['preferred_meals'].queryset = filtered

    def clean_first_delivery_date(self):
        """Allow only Mondays to select."""
        date = self.cleaned_data['first_delivery_date']

        if date.weekday() != DaysOfWeek.MONDAY:
            raise forms.ValidationError(
                "Only Mondays are available for selection."
            )

        return date
