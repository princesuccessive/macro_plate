from django import forms

from apps.core.forms import CrispyFormWithoutTagMixin, NoEditableIdFormMixin
from apps.macroplate.models import PlanType


class PlanTypeForm(
    NoEditableIdFormMixin,
    CrispyFormWithoutTagMixin,
    forms.ModelForm,
):
    """Form for editing plan type."""

    class Meta:
        model = PlanType
        fields = (
            'id',
            'name',
        )

    name = forms.CharField()
