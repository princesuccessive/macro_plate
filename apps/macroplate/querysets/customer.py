import datetime

from django.db import models
from django.db.models import Case, F, OuterRef, Q, Subquery, Sum, Value, When
from django.db.models.functions import Coalesce, Concat
from django.utils import timezone

from apps.core.constants import DaysOfWeek
from apps.core.utils import get_week_end
from apps.macroplate import models as macroplate_models


class CustomerQuerySet(models.QuerySet):
    """Customer Query Set."""

    def has_dishes_for_date(self, date: datetime.date):
        """Select users who have dishes for specified date."""
        return self.filter(
            assignedmenu__daily_menu__date=date,
            assignedmenu__assigned_meals__isnull=False,
        ).distinct()

    def for_delivery(self, date: datetime.date):
        """Select customers with first delivery before the end of this week."""
        sunday = get_week_end(date)

        return self.filter(
            Q(last_delivery_date=None) | Q(last_delivery_date__gte=sunday),
            meal_assignment_paused=False,
            first_delivery_date__lte=sunday,
        )

    def order_display(self):
        """Order for display."""
        return self.order_by(
            'first_name',
            'last_name',
            'first_delivery_date',
            'plan_priority',
        )

    def with_full_name(self):
        """Annotate queryset with full name in format `FirstName LastName`."""
        return self.annotate(
            _full_name=Concat(
                'first_name',
                Value(' '),
                'last_name',
            )
        )

    def with_status(self):
        """Annotate queryset with status.

        Indicates whether the customer is active now (C - current)
        or will be active in the future: one week later (W1 - week 1) or
        two+ weeks later (W2 - week 2).
        """
        today = timezone.now().date()
        last_monday = today - datetime.timedelta(days=today.weekday())
        week_1_monday = last_monday + datetime.timedelta(days=7)
        week_2_monday = week_1_monday + datetime.timedelta(days=7)

        return self.annotate(
            _status=Case(
                When(
                    Q(first_delivery_date__lte=last_monday) & (
                        Q(last_delivery_date__isnull=True) |
                        Q(last_delivery_date__gte=today)
                    ),
                    then=Value(macroplate_models.CustomerStatus.CURRENT),
                ),
                When(
                    first_delivery_date__gte=week_1_monday,
                    first_delivery_date__lt=week_2_monday,
                    then=Value(macroplate_models.CustomerStatus.WEEK_1),
                ),
                When(
                    first_delivery_date__gte=week_2_monday,
                    then=Value(macroplate_models.CustomerStatus.WEEK_2),
                ),
                output_field=models.CharField(),
                default=Value(macroplate_models.CustomerStatus.INACTIVE),
            ),
        )

    def all_latest(self):
        """All latest, including paused."""
        return self.filter(latest=None)

    def history(self):
        """Return old not paused customers."""
        return self.exclude(latest=None)

    def get_old_customer(
        self,
        customer_id: int,
        first_delivery_date: datetime.date,
    ) -> 'macroplate_models.Customer':
        """Get old Customer data from the DB."""
        return self.all_latest().filter(
            id=customer_id,
            first_delivery_date__lt=first_delivery_date,
        ).first()

    def display_on_list_view(self):
        """Get Customers to display on list view.

        We do not display outdated Customer info.

        """
        # TODO fix issue with customers that have
        # TODO last_delivery_date < first_delivery_date
        # Exclude customers that have last delivery date before first
        # delivery date. These customers appear unexpectedly and currently
        # we don't know how to reproduce this bug
        bad_dates = Q(last_delivery_date__lte=F('first_delivery_date'))

        return self.exclude(bad_dates).exclude(
            _status=macroplate_models.CustomerStatus.INACTIVE,
        )

    def with_default_dishes_count_for_day_of_week(self, day_of_week: int):
        """Annotate with default breakfast and lunch counts.

        In case of Friday (index 4), also summarize the weekend dishes:
        while dishes can be assigned to weekend days,
        they are actually delivered on Friday.
        """
        default_daily_schedule_qs = macroplate_models.DailySchedule.objects \
            .filter(
                has_delivery=True,
                date=None,
                customer_id=OuterRef('id'),
            )

        if day_of_week == DaysOfWeek.FRIDAY:
            default_daily_schedule_qs = default_daily_schedule_qs.filter(
                day_of_week__gte=day_of_week,
            ).values(
                'customer_id',
            ).annotate(
                breakfasts=Sum('breakfasts'),
                lunches=Sum('lunches'),
            )
        else:
            default_daily_schedule_qs = default_daily_schedule_qs.filter(
                day_of_week=day_of_week,
            )

        breakfasts_subquery = Subquery(
            default_daily_schedule_qs.values('breakfasts')[:1],
            output_field=models.IntegerField(),
        )
        lunches_subquery = Subquery(
            default_daily_schedule_qs.values('lunches')[:1],
            output_field=models.IntegerField(),
        )

        return self.annotate(
            breakfasts_count=Coalesce(breakfasts_subquery, 0),
            lunches_count=Coalesce(lunches_subquery, 0),
        )

    def prefetch_default_daily(self):
        """Prefetch default DailySchedule data for customers."""
        default_daily_schedule_qs = macroplate_models.DailySchedule.objects \
            .only_default()

        return self.prefetch_related(
            models.Prefetch(
                lookup='daily_schedules',
                queryset=default_daily_schedule_qs,
                to_attr='default_daily_schedules',
            ),
        )
