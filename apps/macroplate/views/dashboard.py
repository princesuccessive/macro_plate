from django.shortcuts import redirect, render
from django.utils import dateformat, timezone

from apps.core.views import BaseView
from apps.macroplate import forms
from apps.macroplate.models import AssignedMenu


class DashboardSelectView(BaseView):
    """View to render day select page for dashboard."""
    template = 'dashboard/select-day.html'

    form_date_select = forms.WorkdaySelectForm

    def render(self, **context):
        """Render page with come context and default forms."""
        return render(self.request, self.template, context=context)

    def get(self, request, *args, **kwargs):
        """Render the schedule page."""
        return self.render(form_date_select=self.form_date_select(initial={
            'date': timezone.now().date(),
        }))

    def post(self, request, *args, **kwargs):
        """Redirect user to dashboard page."""
        form_select = self.form_date_select(self.request.POST)
        if form_select.is_valid():
            date = form_select.cleaned_data.get('date')
            return redirect('dashboard', date=date)

        return self.render(form_date_select=form_select)


class DashboardView(BaseView):
    """View to render dashboard page.

    On this page there are buttons to download some exports.
    """

    def dispatch(self, request, *args, **kwargs):
        """Validate the date, and if it's invalid - redirect user."""
        if not kwargs.get('date'):
            return redirect('dashboard-select')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, date):
        """Add current and next dates to context, and render page."""
        menus = AssignedMenu.objects.filter(daily_menu__date=date)
        assigned = menus.exists()
        has_issues = menus.filter(has_issues=True).exists()

        return render(request, 'dashboard/index.html', context={
            'date': dateformat.format(date, "Y-m-d"),
            'assigned': assigned,
            'has_issues': has_issues,
        })
