from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView


class BaseView(LoginRequiredMixin, View):
    """Base View.

    Requires login.

    """
    pass


class BaseListView(LoginRequiredMixin, ListView):
    """Base List View.

    Requires login.

    """
    pass


class BaseDetailView(LoginRequiredMixin, DetailView):
    """Base Detail View.

    Requires login.

    """
    pass


class BaseCreateView(LoginRequiredMixin, CreateView):
    """Base Create View.

    Requires login.

    """
    pass


class BaseDeleteView(LoginRequiredMixin, DeleteView):
    """Base Delete View.

    Requires login.

    """
    pass


class BaseUpdateView(LoginRequiredMixin, UpdateView):
    """Base Update View.

    Requires login.

    """
    pass
