import datetime

from apps.celery.utils import update_task_progress
from apps.core.constants import WEEKDAYS, DaysOfWeek
from apps.macroplate.models import Customer, DailySchedule


def create_schedules_for_day(date: datetime.date):
    """Create daily schedules for specific day."""
    day_of_week = date.weekday()

    # get all users who have the first date this week or earlier.
    customers = Customer.objects.for_delivery(date) \
        .with_default_dishes_count_for_day_of_week(day_of_week)

    schedules_for_this_day = DailySchedule.objects.filter(date=date)
    count_before = schedules_for_this_day.count()

    # Remove daily schedules for customers not in delivery
    schedules_for_this_day.exclude(customer__in=customers).delete()

    batch = []
    total = customers.count()
    for num, customer in enumerate(customers, 1):

        batch.append(
            DailySchedule(
                customer_id=customer.id,
                day_of_week=day_of_week,
                date=date,
                breakfasts=customer.breakfasts_count,
                lunches=customer.lunches_count,
            )
        )
        update_task_progress(total=total, current=num)

    DailySchedule.objects.bulk_create(batch, ignore_conflicts=True)
    count_now = schedules_for_this_day.count()
    return {
        "total": total,
        "created": count_now - count_before,
        "skipped": count_before,
    }


def create_or_update_defaults(
    customer: Customer,
    customized_days: dict,
):
    """Create a default DailySchedule object for each week day.

    Fill with provided customized schedule data, use default for non-provided.

    Move weekend meals to Friday for Weekly Schedule.
    During meal assignment, when creating date-specific Daily Schedules,
    weekend meals are also moved to Friday. But for default Daily Schedules,
    store weekend data.

    """
    day_of_week_to_daily_schedule = {}
    default_daily_schedule = {
        'has_delivery': False,
        'breakfasts': 0,
        'lunches': 0,
    }

    for day_name, daily_schedule in customized_days.items():
        day_of_week: int = DaysOfWeek.day_index(day_name=day_name)
        day_of_week_to_daily_schedule[day_of_week] = daily_schedule

    for day_of_week in WEEKDAYS:
        daily_schedule: dict = day_of_week_to_daily_schedule.get(
            day_of_week,
            default_daily_schedule,
        )
        DailySchedule.objects.update_or_create(
            customer=customer,
            date=None,
            day_of_week=day_of_week,
            defaults=daily_schedule,
        )
