from django.template.loader import render_to_string

from crispy_forms.layout import TEMPLATE_PACK, LayoutObject


class Formset(LayoutObject):
    """Formset for render a custom formset.

    Based on this implementation:
    https://stackoverflow.com/a/22053952/9728623
    """
    template = 'formset/formset.html'

    def __init__(self, formset_name_in_context, template=None):
        """Accept context name variable, to use it during render."""
        self.formset_name_in_context = formset_name_in_context
        self.fields = []
        if template:
            self.template = template

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK):
        """Pick formset from the outside context, use it to render template."""
        formset = context[self.formset_name_in_context]
        return render_to_string(self.template, {'formset': formset})
