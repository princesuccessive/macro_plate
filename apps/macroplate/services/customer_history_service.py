import datetime

from django.conf import settings
from django.db.models import Q, signals
from django.utils import timezone

import pytz
from factory.django import mute_signals

from apps.core.utils import get_week_start
from apps.macroplate.models import AssignedMenu, DailySchedule

ONE_WEEK = datetime.timedelta(days=7)
TWO_WEEKS = datetime.timedelta(days=14)
ONE_DAY = datetime.timedelta(days=1)


def create_historical_data(customer: 'Customer'):
    """Create historical data for Customer.

    For customers, that are already in delivery, we need to apply changes not
    immediately, but at some particular time.

    * If a Customer updated before 12:00pm Wednesday Pacific Time, changes take
    effect starting next Monday.
    * If a Customer updated after 12:00pm Wednesday Pacific Time, changes take
    effect starting Monday after next.

    Example:
        Customer A with `first_delivery_date` = June 29th with preferences
        `pref 1` and `pref 2`.

        * If Customer A updated with `pref 3` at 11:59am July 8th (Wednesday),
        meals will be assigned with pref 1-3 since July 13th (Monday).
        For delivery at the period July 8th-12th, a historical copy of
        Customer A with pref 1-2 is used.

        * If Customer A updated with `pref 3` at 12:01pm July 8th (Wednesday),
        meals will be assigned with pref 1-3 since July 20th (Monday).
        For delivery at the period July 8th-19th, a historical copy of
        Customer A with pref 1-2 is used.

    If a Customer`s `first_delivery_date` is after the day when changes must
    take effect, we do not create historical copy of old Customer data.

    """
    updated_at = customer.updated_at or timezone.now()
    wednesday_12_pm = _get_wednesday_12_pm(updated_at)

    allow_since = get_week_start(updated_at.date())
    shift = ONE_WEEK if updated_at <= wednesday_12_pm else TWO_WEEKS
    allow_since += shift

    old = _get_old_customer(customer, allow_since)

    if customer.first_delivery_date <= allow_since:
        # Additionally, check existence of such customer with
        # Create historical data for Customer
        if old:
            _save_customer_history(customer, old, allow_since)
        # Set new `first_delivery_date` when Customer's updates should take
        # effect
        customer.first_delivery_date = allow_since


def _get_wednesday_12_pm(date: datetime.date):
    """Get Wednesday 12 pm in client ZT of the same week as the passed date.

    All datetime values are kept in the DB in UTC timezone. So we convert
    12 p.m. in client TZ into UTC and use this value for computations.

    """
    client_tz = pytz.timezone(settings.CLIENT_TZ)

    wednesday_12_pm = datetime.datetime.combine(
        date=get_week_start(date) + datetime.timedelta(days=2),
        time=datetime.time(hour=12, minute=0),
    )
    # Get Wednesday 12 pm in client TZ
    wednesday_12_pm = client_tz.normalize(client_tz.localize(wednesday_12_pm))
    # Convert to UTC
    return wednesday_12_pm.astimezone(pytz.utc)


def _get_old_customer(
    customer: 'Customer',
    allow_since: datetime.date,
) -> 'Customer':
    """Get old Customer data from the DB."""
    return customer._meta.model.objects.get_old_customer(
        customer_id=customer.id,
        first_delivery_date=allow_since,
    )


# Mute `post_save` signal for Customer model to prevent creation of default
# Week and Daily Schedules for the historical Customer data
# and instead copy them from the actual Customer
@mute_signals(signals.post_save)
def _save_customer_history(
    customer: 'Customer',
    old: 'Customer',
    active_until: datetime.date,
):
    """Create historical copy of Customer data for meal assignment."""
    # Get M2M data to save it later
    old_preferences = old.preferences.all()
    old_excluded_meals = old.excluded_meals.all()
    old_preferred_meals = old.preferred_meals.all()

    old.id = None
    old.external_id = None
    old.latest = customer
    # Set the last date when historical data of Customer is used for meal
    # assignment
    old.last_delivery_date = (active_until - ONE_DAY)
    old.save()

    # Save M2M data from old version of Customer
    old.preferences.add(*old_preferences)
    old.excluded_meals.add(*old_excluded_meals)
    old.preferred_meals.add(*old_preferred_meals)

    # Copy daily schedules if exists
    schedules = DailySchedule.objects.filter(
        Q(date=None) | Q(date__lt=active_until),
        customer=customer,
    )
    for schedule in schedules:
        schedule.pk = None
        schedule.customer = old
        schedule.save()

    # Reassign assigned menus
    assigned_menus = AssignedMenu.objects.select_related('daily_menu').filter(
        daily_menu__date__lt=active_until,
        customer=customer,
    )
    for menu in assigned_menus:
        menu.customer = old
        menu.save()
