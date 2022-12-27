from django.urls import reverse_lazy

from apps.core import views
from apps.macroplate import forms

from ..models import Preference


class PreferenceListView(views.BaseListView):
    """Renders list of Preferences."""
    model = Preference
    context_object_name = 'preference_list'
    queryset = Preference.objects.order_by('name').prefetch_related(
        'customers',
        'ingredients',
    )
    template_name = 'preferences/list.html'


class PreferenceCreateView(views.BaseCreateView):
    """Renders Preference creation page.

    Redirects to Preferences list after creation.

    """
    model = Preference
    context_object_name = 'preference'
    form_class = forms.PreferenceForm
    template_name = 'preferences/edit.html'
    success_url = reverse_lazy('preference-list')


class PreferenceUpdateView(views.BaseUpdateView):
    """Renders Preference details.

    Redirects to Preferences list after edition.

    """
    model = Preference
    context_object_name = 'preference'
    form_class = forms.PreferenceForm
    template_name = 'preferences/edit.html'
    success_url = reverse_lazy('preference-list')


class PreferenceDeleteView(views.BaseDeleteView):
    """Renders Preference details.

    Redirects to Preferences list after deletion.

    """
    model = Preference
    context_object_name = 'preference'
    template_name = 'preferences/confirm_delete.html'
    success_url = reverse_lazy('preference-list')
