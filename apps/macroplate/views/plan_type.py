from django.urls import reverse_lazy

from apps.core import views
from apps.macroplate import forms

from ..models import Customer, PlanType


class PlanTypeListView(views.BaseListView):
    """Renders list of Plan types."""
    model = PlanType
    context_object_name = 'plan_type_list'
    queryset = PlanType.objects.order_by('name')
    template_name = 'plan_types/list.html'


class PlanTypeCreateView(views.BaseCreateView):
    """Renders Plan types creation page.

    Redirects to Plan types list after creation.

    """
    model = PlanType
    form_class = forms.PlanTypeForm
    context_object_name = 'plan_type'
    template_name = 'plan_types/edit.html'
    success_url = reverse_lazy('plan-type-list')


class PlanTypeUpdateView(views.BaseUpdateView):
    """Renders Plan types details.

    Redirects to Plan types list after edition.

    """
    model = PlanType
    form_class = forms.PlanTypeForm
    context_object_name = 'plan_type'
    template_name = 'plan_types/edit.html'
    success_url = reverse_lazy('plan-type-list')


class PlanTypeDeleteView(views.BaseDeleteView):
    """Renders Plan types details.

    Redirects to Plan types list after deletion.

    """
    model = PlanType
    context_object_name = 'plan_type'
    template_name = 'plan_types/confirm_delete.html'
    success_url = reverse_lazy('plan-type-list')

    def get_context_data(self, **kwargs):
        """Add list of customers to """
        ctx = super().get_context_data(**kwargs)
        ctx['customers'] = Customer.objects.all_latest().filter(
            plan_type=self.object,
        )
        return ctx
