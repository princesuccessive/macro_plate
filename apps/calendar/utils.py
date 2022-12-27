import datetime
import typing

from apps.macroplate.models import DailySchedule


def get_scheduled_meals_for_date(
    date: datetime.datetime,
    breakfasts: int,
    lunches: int,
    custom: bool,
) -> typing.List[dict]:
    """Get list of scheduled meals for specific date to display in calendar.

    For example, for params:
        date = 2020-01-30,
        breakfasts=1,
        lunches=2,
        custom=False,

    And you will get:
        [
            {date: 2020-01-30, custom: false, type: 'breakfast', id: <ID>},

            {date: 2020-01-30, custom: false, type: 'lunch', id: <ID>},
            {date: 2020-01-30, custom: false, type: 'lunch', id: <ID>},
        ]

    <ID> generated by next template {date}-{meal_type}-{number}
    generated ID must be unique and not changing

    """
    config = [
        ('breakfast', breakfasts),
        ('lunch', lunches),
    ]

    result = []
    for meal_type, count in config:
        for i in range(count):
            item = {
                'id': f'{date}-{meal_type}-{i}',
                'date': date,
                'custom': custom,
                'type': meal_type
            }
            result.append(item)
    return result


def get_custom_daily_schedules_by_date(customer_id, date_from, date_to):
    """Get custom DailySchedules for date range, converted to dict.

    This method returns dictionary, where key it's date, and value it's
    custom Daily schedule for this date.
    """
    custom_schedules = DailySchedule.objects.filter(
        customer_id=customer_id,
        date__gte=date_from,
        date__lte=date_to,
        has_delivery=True,
    )
    return {schedule.date: schedule for schedule in custom_schedules}


def get_default_daily_schedules_by_workday(customer_id):
    """Get default DailySchedules for date range, converted to dict.

    This method returns dictionary, where key it's day of week, and value it's
    default Daily schedule for this day of week.
    """
    default_schedules = DailySchedule.objects.filter(
        customer_id=customer_id,
        date=None,
        has_delivery=True,
    )
    return {schedule.day_of_week: schedule for schedule in default_schedules}