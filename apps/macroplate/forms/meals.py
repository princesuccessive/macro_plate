from crispy_forms import layout as crispy_layout

from apps.core.forms import EditionFormWithFormset
from apps.core.formset.custom_layout_object import Formset
from apps.macroplate.models import Meal


class MealForm(EditionFormWithFormset):
    """Meal edition form.

    Displays all fields and inline form for ingredients.

    """

    class Meta:
        model = Meal
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = crispy_layout.Layout(
            crispy_layout.Div(
                crispy_layout.Field('name'),
                crispy_layout.Field('plan_type'),
                crispy_layout.Field('breakfast'),
                crispy_layout.Div(
                    crispy_layout.Fieldset(
                        'Ingredients',
                        Formset('ingredients')
                    ),
                    css_class='mt-2',
                ),
                crispy_layout.Div(
                    crispy_layout.Fieldset(
                        'Modifiers',
                        Formset('mods')
                    ),
                    css_class='mt-2',
                ),
                crispy_layout.HTML('<br>'),
                crispy_layout.ButtonHolder(
                    crispy_layout.Submit('submit', 'Save Meal')
                ),
            )
        )
