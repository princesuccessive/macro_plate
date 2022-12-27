from django import forms
from django.utils import timezone

from bootstrap_datepicker_plus import DatePickerInput

from apps.core.constants import DEFAULT_DATEPICKER_OPTIONS, WORKDAYS
from apps.core.utils import get_nearest_work_day


class WorkdaySelectForm(forms.Form):
    """Form for select work day."""

    date = forms.DateField(
        label="Date",
        widget=DatePickerInput(**DEFAULT_DATEPICKER_OPTIONS)
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.fields['date'].initial:
            workday = get_nearest_work_day(timezone.now().date())
            self.fields['date'].initial = workday

    def clean_date(self):
        """Check that selected day is Work day."""
        date = self.cleaned_data['date']

        if date.weekday() not in WORKDAYS:
            raise forms.ValidationError("Please select work day!")
        return date
