from crispy_forms import layout as crispy_layout

from apps.core.forms import EditionFormWithFormset
from apps.core.formset.custom_layout_object import Formset
from apps.macroplate.models import AssignedMenu


class AssignedMenuForm(EditionFormWithFormset):
    """AssignedMenu edition form."""

    class Meta:
        model = AssignedMenu
        fields = (
            'has_issues',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = crispy_layout.Layout(
            crispy_layout.Div(
                crispy_layout.Fieldset(
                    '',
                    Formset('assigned_meals')
                ),
            )
        )
