from django import forms


class CsvFileUploadForm(forms.Form):
    """Form for upload a csv-file."""

    file = forms.FileField(label='CSV-file')
    clear_customers = forms.BooleanField(
        label='Clear customers',
        required=False,
    )

    # TODO(Dontsov): Add csv validation
