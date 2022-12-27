from django import forms

from crispy_forms import layout as crispy_layout
from crispy_forms.helper import FormHelper

from ..models import Ingredient


class IngredientForm(forms.ModelForm):
    """Ingredients edition form."""

    class Meta:
        model = Ingredient
        fields = (
            'name',
            'quantity_type',
            'is_protein',
            'count',
            'preferences',
            'conversion_raw',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'row'
        self.helper.layout = crispy_layout.Layout(
            crispy_layout.Div(
                crispy_layout.Field('name', required=True),
                css_class='col-12',
            ),
            crispy_layout.Div(
                crispy_layout.Field('quantity_type'),
                crispy_layout.Field('is_protein'),
                crispy_layout.Field('count'),
                crispy_layout.Field('conversion_raw'),
                css_class='col-6',
            ),
            crispy_layout.Div(
                crispy_layout.Field('preferences'),
                css_class='col-6',
            ),
        )
