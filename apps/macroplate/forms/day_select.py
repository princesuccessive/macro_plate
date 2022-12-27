from django import forms
from django.utils import timezone

from bootstrap_datepicker_plus import DatePickerInput

from apps.core.constants import DEFAULT_DATEPICKER_OPTIONS


class DaySelectForm(forms.Form):
    """Form for select day."""

    date = forms.DateField(
        label="Date",
        widget=DatePickerInput(**DEFAULT_DATEPICKER_OPTIONS)
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.fields['date'].initial:
            self.fields['date'].initial = timezone.now().date()
