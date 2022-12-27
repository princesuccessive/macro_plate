import datetime
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.dispatch import Signal
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.macroplate.querysets import CustomerQuerySet


class SnackFrequency:
    """Choices for `Customer.snacks_count` field."""
    NO_SNACKS = 0
    SNACKS_1 = 1
    SNACKS_2 = 2
    SNACKS_3 = 3
    SNACKS_4 = 4
    SNACKS_5 = 5
    SNACKS_6 = 6
    SNACKS_7 = 7
    SNACKS_8 = 8
    SNACKS_9 = 9

    CHOICES = (
        (NO_SNACKS, _('No snacks')),
        (SNACKS_1, _('1/day')),
        (SNACKS_2, _('2/day')),
        (SNACKS_3, _('3/day')),
        (SNACKS_4, _('4/day')),
        (SNACKS_5, _('5/day')),
        (SNACKS_6, _('6/day')),
        (SNACKS_7, _('7/day')),
        (SNACKS_8, _('8/day')),
        (SNACKS_9, _('9/day')),
    )


class JuiceFrequency:
    """Choices for `Customer.juice_count` field."""
    NO_JUICE = 0
    JUICE_1 = 1
    JUICE_2 = 2
    JUICE_3 = 3
    JUICE_4 = 4
    JUICE_5 = 5
    JUICE_6 = 6
    JUICE_7 = 7
    JUICE_8 = 8
    JUICE_9 = 9

    CHOICES = (
        (NO_JUICE, _('No juice')),
        (JUICE_1, _('1/week')),
        (JUICE_2, _('2/week')),
        (JUICE_3, _('3/week')),
        (JUICE_4, _('4/week')),
        (JUICE_5, _('5/week')),
        (JUICE_6, _('6/week')),
        (JUICE_7, _('7/week')),
        (JUICE_8, _('8/week')),
        (JUICE_9, _('9/week')),
    )


class PlanPriority:
    """Choices for `Customer.priority` field."""
    PRIMARY = 'primary'
    SECONDARY = 'secondary'

    CHOICES = (
        (PRIMARY, _('Primary')),
        (SECONDARY, _('Secondary')),
    )


class CustomerStatus:
    """Choices for `Customer.status` property/annotation."""
    CURRENT = 'C'
    WEEK_1 = 'W1'
    WEEK_2 = 'W2'
    INACTIVE = 'INACTIVE'


create_history = Signal(providing_args=['instance', ])
create_history.__doc__ = (
    'Signal means that historical data for a Customer should be created'
)


class Customer(models.Model):
    """Customer model.

    NOTE: the model previously included two more PositiveSmallIntegerFields:
    `dishes_per_day` and `five_or_seven_days`, which were used to build
    DailySchedule objects. But now the customers API allows direct control
    over daily schedule, so we have no need for these fields.
    """
    external_id = models.CharField(
        verbose_name=_('External ID'),
        max_length=50,
        unique=True,
        editable=False,
    )

    # Personal Info
    first_name = models.CharField(
        verbose_name=_('First Name'),
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name=_('Last Name'),
        max_length=150,
    )
    email = models.EmailField(
        verbose_name=_('Email'),
    )
    phone_number = models.CharField(
        verbose_name=_('Phone Number'),
        max_length=30,
    )

    # Delivery Info
    address = models.TextField(
        max_length=255,
        blank=True,
        verbose_name=_('Address'),
    )
    suite = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Suite'),
    )
    city = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('City'),
    )
    zip = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Zip'),
    )
    first_delivery_date = models.DateField(
        verbose_name=_('First Delivery'),
    )
    delivery_notes = models.TextField(
        max_length=350,
        blank=True,
        verbose_name=_('Delivery Notes'),
    )
    delivery_window = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_('Delivery Window'),
    )
    red = models.BooleanField(
        default=False,
        verbose_name=_('RED')
    )

    # Plan Info
    plan_type = models.ForeignKey(
        'PlanType',
        verbose_name=_('Plan Type'),
        on_delete=models.PROTECT,
        related_name='customers',
    )
    # TODO (Khaziev): all prod customers are `primary`; consider deleting
    plan_priority = models.CharField(
        max_length=20,
        choices=PlanPriority.CHOICES,
        default=PlanPriority.PRIMARY,
        verbose_name=_('Plan Priority'),
    )

    # Protein snack info
    snacks_count = models.PositiveSmallIntegerField(
        choices=SnackFrequency.CHOICES,
        default=SnackFrequency.NO_SNACKS,
        verbose_name=_('Snacks Count')
    )
    snacks_notes = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_('Snacks Notes'),
    )
    gluten_free = models.BooleanField(
        default=False,
        verbose_name=_('Gluten Free?'),
    )
    nut_free = models.BooleanField(
        default=False,
        verbose_name=_('Nut Free?'),
    )

    # Cold Pressed Juice Info
    juice_count = models.PositiveSmallIntegerField(
        choices=JuiceFrequency.CHOICES,
        default=JuiceFrequency.NO_JUICE,
        verbose_name=_('Juice Count'),
    )
    juice_requested = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_('Juice Requested'),
    )
    juice_dislikes = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_('Juice Dislikes'),
    )

    coffee_count = models.SmallIntegerField(
        default=0,
        verbose_name=_('Coffee Count'),
        validators=(MinValueValidator(0), MaxValueValidator(30),)
    )

    # Preferences Info
    preferences = models.ManyToManyField(
        'Preference',
        through='CustomerPreference',
        related_name='customers',
        blank=True,
    )
    preferences_notes = models.TextField(
        blank=True,
        verbose_name=_('Preferences Notes'),
    )

    promo_code = models.CharField(
        default='',
        max_length=30,
        blank=True,
        verbose_name=_('Promo code'),
    )

    # Pausing of meal assignment
    meal_assignment_paused = models.BooleanField(
        default=False,
        verbose_name=_('Pause meal assignment?'),
    )

    excluded_meals = models.ManyToManyField(
        'Meal',
        related_name='excluded_meals',
        blank=True,
        verbose_name=_('Meals Exclusion'),
    )

    preferred_meals = models.ManyToManyField(
        'Meal',
        related_name='preferred_meals',
        blank=True,
        verbose_name=_('Preferred Meals'),
    )

    carbs = models.TextField(
        max_length=255,
        blank=True,
        verbose_name=_('Carbs'),
    )
    protein = models.TextField(
        max_length=255,
        blank=True,
        verbose_name=_('Protein'),
    )
    fat = models.TextField(
        max_length=255,
        blank=True,
        verbose_name=_('Fat'),
    )

    # Fields for historical data purposes
    latest = models.ForeignKey(
        'Customer',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='history',
    )
    last_delivery_date = models.DateField(
        verbose_name=_('Last Delivery'),
        blank=True,
        null=True,
    )

    updated_at = models.DateTimeField(
        verbose_name=_('Updated at'),
        blank=True,
        null=True,
    )

    objects = CustomerQuerySet.as_manager()

    # all the fields, unrelated to meals and planning, which is kept the same
    # for current and historical instances
    PERSONAL_AND_DELIVERY_INFO = (
        'first_name',
        'last_name',
        'email',
        'phone_number',
        'address',
        'suite',
        'city',
        'zip',
        'delivery_notes',
        'delivery_window',
        'red',
        'promo_code',
    )

    def __str__(self):
        if self.meal_assignment_paused:
            return f'{self.full_name} (Paused)'
        return self.full_name

    @property
    def full_name(self):
        """Return Customer full name."""
        if hasattr(self, '_full_name'):
            return self._full_name
        return f'{self.first_name} {self.last_name}'

    @property
    def plan_string(self):
        """Return play_type_id.

        Previously would return a string of this format:
        `{plan_type_id}-{dishes_per_day}-{five_or_seven_days}`, for example
        'trad-3-7'. But the rest of fields is now removed.
        """
        return self.plan_type_id

    @property
    def preferences_names(self):
        """Get string with names of preferences."""
        preferences = self.preferences.values_list('name', flat=True)
        return ', '.join(preferences)

    @property
    def is_active(self):
        """Return if Customer is active - when meal assignment not paused."""
        return not self.meal_assignment_paused

    @property
    def status(self) -> str:
        """Annotate queryset with status.

        Indicates whether it is active now (C - current) or will be active in
        the future: one week later (W1 - week 1) or two+ weeks later
        (W2 - week 2).

        """
        if hasattr(self, '_status'):
            return self._status

        today = timezone.now().date()
        last_monday = today - datetime.timedelta(days=today.weekday())
        week_1_monday = last_monday + datetime.timedelta(days=7)
        week_2_monday = week_1_monday + datetime.timedelta(days=7)

        is_current = (
            self.first_delivery_date <= last_monday and
            (self.last_delivery_date is None or self.last_delivery_date >= today)  # noqa
        )
        is_week_1 = week_1_monday <= self.first_delivery_date < week_2_monday
        is_week_2 = self.first_delivery_date >= week_2_monday

        if is_current:
            return CustomerStatus.CURRENT

        if is_week_1:
            return CustomerStatus.WEEK_1

        if is_week_2:
            return CustomerStatus.WEEK_2

        return CustomerStatus.INACTIVE

    def clean(self):
        """Forbid edition of historical Customer data."""
        if self.latest_id:
            raise ValidationError('You are not allowed to edit historical')

    def clean_delivery_date(self):
        """Check last delivery date.

        Somehow we have Customers with Last delivery date earlier that First
        delivery date. This check added to catch the case, and then fix it.
        TODO: Remove after the problem solved

        """
        if (self.last_delivery_date
                and self.last_delivery_date < self.first_delivery_date):
            raise ValidationError(
                'Last delivery date cannot be earlier than First delivery date'
            )

    def save(self, *args, **kwargs):
        """Run extra actions before saving.

        * Add external ID for user, if not specified.

        For current(non-historical) existing data:
        * Create historical data if required.
        * Update all historical data with current personal info.

        """
        # Check last delivery date for historical copy of Customer.
        # This check is placed here because historical data created internally
        # inside Customer.save method.
        self.clean_delivery_date()

        if not self.external_id:
            self.external_id = uuid4()

        # Do not create historical data for new Customers
        # Create historical data only for the actual Customers data
        if not self.latest_id and self.id:
            create_history.send(sender=self.__class__, instance=self)

            new_personal_info = {
                key: getattr(self, key)
                for key in self.PERSONAL_AND_DELIVERY_INFO
            }
            self.history.update(**new_personal_info)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Delete historical data before the Customer deletion."""
        if not self.latest_id:
            for historical in self.history.history():
                historical.delete()

        super().delete(*args, **kwargs)


class CustomerPreference(models.Model):
    """Custom `through` model for M2M Customer and Preference."""
    customer = models.ForeignKey(
        'Customer',
        on_delete=models.CASCADE,
    )
    preference = models.ForeignKey(
        'Preference',
        on_delete=models.CASCADE,
    )
    from_api = models.BooleanField(
        verbose_name=_('From API'),
        default=False,
    )
