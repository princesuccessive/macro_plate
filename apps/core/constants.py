import calendar
from decimal import Decimal

from django.utils.translation import gettext_lazy as _


class DaysOfWeek:
    """Days of week."""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    CHOICES_WORKDAYS = (
        (MONDAY, _('Monday')),
        (TUESDAY, _('Tuesday')),
        (WEDNESDAY, _('Wednesday')),
        (THURSDAY, _('Thursday')),
        (FRIDAY, _('Friday')),
    )

    CHOICES = CHOICES_WORKDAYS + (
        (SATURDAY, _('Saturday')),
        (SUNDAY, _('Sunday')),
    )

    STR_TO_INDEX_MAP = {
        day_of_week: index for index, day_of_week in enumerate((
            'monday',
            'tuesday',
            'wednesday',
            'thursday',
            'friday',
            'saturday',
            'sunday',
        ))
    }

    @staticmethod
    def day_name(day):
        """Get weekday name by number."""
        return calendar.day_name[day]

    @classmethod
    def day_index(cls, day_name: str) -> int:
        """Get weekday number by weekday name."""
        return cls.STR_TO_INDEX_MAP[day_name.lower()]


# Days on which MacroPlate perform delivery.
WORKDAYS = [
    DaysOfWeek.MONDAY,
    DaysOfWeek.TUESDAY,
    DaysOfWeek.WEDNESDAY,
    DaysOfWeek.THURSDAY,
    DaysOfWeek.FRIDAY,
]
WEEKEND = {
    DaysOfWeek.SATURDAY,
    DaysOfWeek.SUNDAY,
}
WEEKDAYS = {
    *WORKDAYS,
    *WEEKEND,
}


class QuantityType:
    """Contains measure units."""
    COUNT = 'ct'
    OUNCE = 'oz'
    GRAM = 'g'
    KILO = 'kg'
    POUND = 'lb'
    GALLON = 'us_g'
    QUART = 'us_qt'
    PINT = 'us_pint'
    CUP = 'us_cup'
    FLUID_OUNCE = 'us_oz'
    TABLESPOON = 'us_tbsp'
    TEASPOON = 'us_tsp'
    MILLILITER = 'ml'
    LITER = 'l'
    BUSHEL = 'bsh'

    CHOICES = (
        (COUNT, _('Count')),
        (OUNCE, _('Ounce(s)')),
        (GRAM, _('Gram(s)')),
        (KILO, _('Kilogram(s)')),
        (POUND, _('Pound(s) (lbs)')),
        (GALLON, _('Gallon(s)')),
        (QUART, _('Quart(s)')),
        (PINT, _('Pint(s)')),
        (CUP, _('Cup(s)')),
        (FLUID_OUNCE, _('Fluid Ounce(s)')),
        (TABLESPOON, _('Tablespoon(s) ')),
        (TEASPOON, _('Teaspoon(s)')),
        (MILLILITER, _('Milliliter(s)')),
        (LITER, _('Liter(s)')),
        (BUSHEL, _('Bushel(s)')),
    )


# Conversion coefficient from OUNCE to POUND
OUNCE_TO_POUND = Decimal(0.0625)
FINAL_LBS_COEFFICIENT = Decimal(1.1)


DEFAULT_DATEPICKER_OPTIONS = dict(
    format='%Y-%m-%d',
    options={
        'daysOfWeekDisabled': [0, 6],
        'showClear': False,
    },
)
