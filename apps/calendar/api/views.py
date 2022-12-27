from collections import Counter, defaultdict

from django.utils.dateparse import parse_date

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.macroplate.models import AssignedMeal, Customer, DailySchedule

from ...core.constants import WORKDAYS
from ...core.utils import date_range
from ..utils import (
    get_custom_daily_schedules_by_date,
    get_default_daily_schedules_by_workday,
    get_scheduled_meals_for_date,
)
from .serializers import (
    AssignedMealForCalendarSerializer,
    CalendarQueryParamsSerializer,
    SaveScheduleSerializer,
)


class CalendarAssignedMealsView(APIView):
    """List all the customers assigned meals to display in the calendar."""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Get list of assigned meals for customer for date range.

        This endpoint requires next query params:
            customer_id - id of the customer
            start - start date
            end - end date
        """
        serializer = CalendarQueryParamsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        customer_id = data.get('customer_id')
        date_from = parse_date(data.get('start'))
        date_to = parse_date(data.get('end'))

        # get customer
        customer = Customer.objects.get(pk=customer_id)

        assigned_meals = AssignedMeal.objects.filter(
            assigned_menu__customer=customer,
            assigned_menu__daily_menu__date__gte=date_from,
            assigned_menu__daily_menu__date__lte=date_to,
        )

        serialized_assigned_meals = AssignedMealForCalendarSerializer(
            assigned_meals,
            many=True
        )

        return Response(serialized_assigned_meals.data)


class CalendarScheduledMealsView(APIView):
    """View for working with the customer's meal schedule in calendar.

    This endoint allow to get and edit only meals scheduled fot today and
    future days.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Get list of scheduled meals for customer for date range.

        This endpoint requires next query params:
            customer_id - id of the customer
            start - start date
            end - end date
        """
        serializer = CalendarQueryParamsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serializer_data = serializer.data

        customer_id = serializer_data.get('customer_id')
        date_from = parse_date(serializer_data.get('start'))
        date_to = parse_date(serializer_data.get('end'))
        today = parse_date(serializer_data.get('today'))

        customer = Customer.objects.get(pk=customer_id)
        first_delivery_date = customer.first_delivery_date

        if date_from < today:
            date_from = today
        if date_from < first_delivery_date:
            date_from = first_delivery_date

        schedule_meals_events = self._get_scheduled_meals(
            customer_id,
            date_from,
            date_to,
        )

        return Response(schedule_meals_events)

    def put(self, request, *args, **kwargs):
        """Update scheduled meals.

        This endpoint accepts elements describing each meal for the current
        date, as well as the date range in which they are defined.
        The date range is necessary to take into account the days from which
        all meals were removed.
        """
        serializer = SaveScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer_data = serializer.data

        date_from = parse_date(serializer_data.get('start'))
        date_to = parse_date(serializer_data.get('end'))
        today = parse_date(serializer_data.get('today'))
        items = serializer_data.get('items')
        customer_id = serializer_data.get('customer_id')

        customer = Customer.objects.get(pk=customer_id)
        first_delivery_date = customer.first_delivery_date

        if date_from < today:
            date_from = today
        if date_from < first_delivery_date:
            date_from = first_delivery_date

        count = self._save_scheduled_meals(
            customer_id=customer_id,
            date_from=date_from,
            date_to=date_to,
            items=items,
        )

        return Response(data={"count": count})

    def _get_scheduled_meals(self, customer_id, date_from, date_to):
        """Get scheduled meals for each day in date range.

        We process all the buyer's schedules over a period of time.
        We consider custom schedules, and if there are none, we use default
        schedules.
        """
        items = []

        # Get days, where assigned meals
        filled_dates = AssignedMeal.objects.filter(
            assigned_menu__customer_id=customer_id,
            assigned_menu__daily_menu__date__gte=date_from,
            assigned_menu__daily_menu__date__lte=date_to,
        ).values_list('assigned_menu__daily_menu__date', flat=True)
        filled_dates = set(filled_dates)

        default_schedules = get_default_daily_schedules_by_workday(customer_id)
        custom_schedules = get_custom_daily_schedules_by_date(
            customer_id=customer_id,
            date_from=date_from,
            date_to=date_to,
        )

        for current_date in date_range(date_from, date_to, workdays_only=True):
            if current_date in filled_dates:
                continue

            default_schedule = default_schedules.get(current_date.weekday())
            custom_schedule = custom_schedules.get(current_date)

            schedule = custom_schedule or default_schedule

            daily_items = get_scheduled_meals_for_date(
                date=current_date,
                breakfasts=schedule.breakfasts,
                lunches=schedule.lunches,
                custom=bool(custom_schedule),
            )
            items.extend(daily_items)
        return items

    def _save_scheduled_meals(self, customer_id, date_from, date_to, items):
        """Save scheduled meals for each day in date range.

        When processing each day, we calculate the total number of dishes for
        each day, and compare it with the schedule. If there is a custom
        schedule, we compare it with it, if not, we compare it with the
        default.
        If the schedules match, we don't do anything. If they differ, we create
        or update a custom schedule for that day.
        """
        # Group items by dates
        groups = defaultdict(Counter)
        for item in items:
            date = parse_date(item.get('date'))
            type = item.get('type')
            groups[date].update([type])

        default_schedules = get_default_daily_schedules_by_workday(customer_id)
        custom_schedules = get_custom_daily_schedules_by_date(
            customer_id=customer_id,
            date_from=date_from,
            date_to=date_to,
        )

        edited_count = 0

        for current_date in date_range(date_from, date_to, workdays_only=True):
            if current_date.weekday() not in WORKDAYS:
                continue

            default_schedule = default_schedules.get(current_date.weekday())
            custom_schedule = custom_schedules.get(current_date)

            # calculate new counter for this day
            new_schedule = groups.get(current_date, {})
            breakfasts = new_schedule.get('breakfast', 0)
            lunches = new_schedule.get('lunch', 0)

            # Compare numbers with schedule for this date
            schedule = custom_schedule or default_schedule
            is_breakfasts_count_equal = schedule.breakfasts == breakfasts
            is_lunches_count_equal = schedule.lunches == lunches

            if is_breakfasts_count_equal and is_lunches_count_equal:
                continue

            edited_count += 1
            DailySchedule.objects.update_or_create(
                customer_id=customer_id,
                date=current_date,
                day_of_week=current_date.weekday(),
                defaults=dict(
                    breakfasts=breakfasts,
                    lunches=lunches,
                )
            )
        return edited_count
