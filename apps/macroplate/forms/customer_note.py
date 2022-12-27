from django import forms

from crispy_forms import layout as crispy_layout

from ...core.forms import CrispyFormWithoutTagMixin
from ..models import Customer, CustomerNote


class CustomerNoteForm(
    CrispyFormWithoutTagMixin,
    forms.ModelForm,
):
    """CustomerNote creation form."""

    class Meta:
        model = CustomerNote
        fields = (
            'customer',
            'title',
            'text',
        )

    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].disabled = True

        self.helper.form_class = 'row'
        self.helper.layout = crispy_layout.Layout(
            crispy_layout.Div(
                crispy_layout.Field('customer', required=False),
                css_class='col-12',
            ),
            crispy_layout.Div(
                crispy_layout.Field('title', required=True),
                css_class='col-12',
            ),
            crispy_layout.Div(
                crispy_layout.Field('text', required=True),
                css_class='col-12',
            ),
        )
