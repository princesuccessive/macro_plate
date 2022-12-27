from django import forms

from apps.core.constants import DaysOfWeek


class DayOfWeekSelectForm(forms.Form):
    """Form for select day of week."""

    day_of_week = forms.ChoiceField(
        label="Day of week",
        choices=DaysOfWeek.CHOICES,
    )
