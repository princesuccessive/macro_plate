from django import forms

from apps.core.forms import CrispyFormWithoutTagMixin, NoEditableIdFormMixin
from apps.macroplate.models import Preference


class PreferenceForm(
    NoEditableIdFormMixin,
    CrispyFormWithoutTagMixin,
    forms.ModelForm,
):
    """Form for editing preference."""

    class Meta:
        model = Preference
        fields = (
            'id',
            'name',
        )

    id = forms.CharField(required=False)
    name = forms.CharField(required=True)
