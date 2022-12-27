from django.shortcuts import get_object_or_404
from django.utils import dateformat
from django.views.generic.base import TemplateView

from apps.core.views import BaseView
from apps.macroplate.models import Customer


class CustomerCalendarView(TemplateView, BaseView):
    """View to show calendar with assigned and scheduled meals for Customer."""
    template_name = 'calendar/calendar.html'

    def get_context_data(self, **kwargs):
        """Extend context with customer data.

        Add customer's first delivery date and default weekly schedule,
        built from default Daily Schedule objects.
        """
        ctx = super().get_context_data(**kwargs)

        customer: Customer = get_object_or_404(
            Customer.objects.prefetch_default_daily(),
            pk=kwargs['customer_id'],
        )

        default_weekly_schedule = {
            daily_schedule.day_of_week: daily_schedule.dishes_count
            for daily_schedule in customer.default_daily_schedules
        }

        first_delivery_date = customer.first_delivery_date
        first_delivery_date = dateformat.format(first_delivery_date, "Y-m-d")

        ctx.update({
            'customer_id': customer.id,
            'default_weekly_schedule': default_weekly_schedule,
            'first_delivery_date': first_delivery_date,
        })
        return ctx
