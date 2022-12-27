from django import forms

from crispy_forms.helper import FormHelper


class CustomControlFormMixin:
    """Default crispy form with empty form helper and custom controls."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not hasattr(self, 'helper'):
            self.helper = FormHelper(self)
        self.helper.use_custom_control = True


class EditionFormWithFormset(forms.ModelForm):
    """Edition Form with Formset for related objects.

    Redefine `self.helper.layout` with a `Formset` to add custom layout.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'


class NoEditableIdFormMixin:
    """Form mixin for not editable `id` field."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # disable changing the ID when editing
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            if 'id' in self.fields:
                self.fields['id'].disabled = True


class CrispyFormWithoutTagMixin:
    """Mixin for removing form tag from crispy form."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not hasattr(self, 'helper'):
            self.helper = FormHelper()
        self.helper.form_tag = False


class LimitEditableFieldsFormMixin:
    """Mixin to limit editable fields (while Updating, not Creating)."""
    # this property true when editing, and false when creating
    edit = None

    class Meta:
        # List of editable fields
        editable_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # if creating - skip checking
        instance = getattr(self, 'instance', None)
        self.edit = instance and instance.pk
        if not self.edit:
            return

        # if editing, disable not editable fields
        for field in self.fields:
            if field not in self.Meta.editable_fields:
                # for checkbox and radio
                self.fields[field].disabled = True
                self.fields[field].widget.attrs['disabled'] = True
                # for other inputs
                self.fields[field].widget.attrs['readonly'] = True
