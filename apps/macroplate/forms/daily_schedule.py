from django import forms

from apps.macroplate.models import DailySchedule


class DailyScheduleForm(forms.ModelForm):
    """DailySchedule form."""

    class Meta:
        model = DailySchedule
        fields = (
            'has_delivery',
            'breakfasts',
            'lunches',
        )
