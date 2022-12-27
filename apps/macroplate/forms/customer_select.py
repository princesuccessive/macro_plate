from datetime import datetime

from django import forms

from apps.macroplate.models import Customer


class CustomerSelectForm(forms.Form):
    """Form to select a customer."""

    customer = forms.ModelChoiceField(
        queryset=Customer.objects.order_display(),
        widget=forms.Select(attrs={
            'class': 'selectpicker',
            'data-live-search': 'true',
            'data-style': 'custom-select-picker',
        })
    )


class CustomerForDeliverySelect(CustomerSelectForm):
    """Form for select a customer."""

    def __init__(self, *args, date: datetime.date, **kwargs):
        super().__init__(*args, **kwargs)
        customers = Customer.objects.for_delivery(date)
        self.fields['customer'].queryset = customers
