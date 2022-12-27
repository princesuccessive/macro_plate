from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from apps.core import views
from apps.macroplate.forms import CustomerNoteForm
from apps.macroplate.models import Customer, CustomerNote


class CustomerNoteCreateView(views.BaseCreateView):
    """Renders CustomerNote creation page.

    Redirects to Customer details after creation.

    """
    model = CustomerNote
    form_class = CustomerNoteForm
    template_name = 'customers/notes/create.html'

    def get_success_url(self):
        return reverse_lazy(
            'customer-detail',
            kwargs=dict(
                pk=self.kwargs['customer_id'],
            ),
        )

    def get_initial(self):
        customer = get_object_or_404(
            Customer.objects.all(),
            id=self.kwargs['customer_id'],
        )

        initial = super().get_initial()
        initial['customer'] = customer.id
        return initial
