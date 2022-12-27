from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from apps.core.views import BaseView


class ProfileView(PasswordChangeView, BaseView):
    """View to render user profile page.

    TODO (Dontsov): This view will be extended in future

    """
    success_url = reverse_lazy('account-profile')
    template_name = 'account/profile.html'
    title = _('Profile')

    def form_valid(self, form):
        """Add message on form submission success."""
        msg = f'Password changed successfully!'
        messages.success(self.request, msg)
        return super().form_valid(form)
