from typing import Optional

from django.contrib import messages
from django.shortcuts import redirect, render

from apps.core.views import BaseUpdateView, BaseView
from apps.macroplate.forms import (
    CustomerAndDayOfWeekSelectForm,
    DailyScheduleForm,
)
from apps.macroplate.models import DailySchedule


class DailyScheduleSelectView(BaseView):
    """View for display and edit Default Daily Schedules."""
    form = CustomerAndDayOfWeekSelectForm
    template = 'schedules/daily/default-select.html'
    NOT_FOUND_MESSAGE = (
        'Schedule not found, please go to the customer settings and update '
        'profile (change frequency) for example.'
    )
    queryset = DailySchedule.objects.filter(date=None)

    def render(self, form):
        """Render the template with context."""
        return render(self.request, self.template, {'form': form})

    def get(self, request, *args, **kwargs):
        """Display form with selecting week and form with schedule."""
        return self.render(form=self.form())

    def post(self, request, *args, **kwargs):
        """Open selected schedule."""
        form = self.form(request.POST)
        if not form.is_valid():
            return self.render(form=form)

        schedule: Optional[DailySchedule] = self.queryset.filter(
            **form.cleaned_data,
        ).first()
        if schedule:
            return redirect(
                to='schedules-daily-default',
                customer_id=schedule.customer_id,
                day_of_week=schedule.day_of_week,
            )

        form.add_error(None, self.NOT_FOUND_MESSAGE)
        return self.render(form=form)


class DailyScheduleView(BaseUpdateView):
    """View for editing Default Daily Schedules."""
    form_select_class = CustomerAndDayOfWeekSelectForm
    form_class = DailyScheduleForm
    template_name = 'schedules/daily/default.html'
    queryset = DailySchedule.objects.filter(date=None)

    @property
    def _customer_id(self) -> int:
        """Get customer ID from URL params."""
        return self.kwargs['customer_id']

    @property
    def _day_of_week(self) -> int:
        """Get day of week from URL params."""
        return self.kwargs['day_of_week']

    def get_object(self, queryset=None):
        """Get assigned menu by customer_id and date."""
        return self.get_queryset().get(
            customer_id=self._customer_id,
            day_of_week=self._day_of_week,
        )

    def get_context_data(self, **kwargs):
        """Prepare context for showing form."""
        context = super().get_context_data(**kwargs)

        context['form_select'] = self.form_select_class(initial={
            'customer': self._customer_id,
            'day_of_week': self._day_of_week,
        })

        return context

    def form_valid(self, form):
        """Show success message."""
        msg = 'The schedule is saved successfully'
        messages.success(self.request, msg)

        self.object = form.save()
        return redirect(
            'schedules-daily-default',
            customer_id=self._customer_id,
            day_of_week=self._day_of_week,
        )
