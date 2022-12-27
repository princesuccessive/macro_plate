from datetime import timedelta

from django.test import TestCase
from django.utils import dateformat, timezone

from apps.calendar.api.views import CalendarScheduledMealsView
from apps.core.utils import get_week_start
from apps.macroplate.factories import CustomerFactory
from apps.macroplate.models import DailySchedule


class TestCalendarScheduleEdit(TestCase):
    """Test for `CalendarScheduledMealsView`."""

    @classmethod
    def setUpTestData(cls):
        cls.today = get_week_start(timezone.now().date()) + timedelta(weeks=1)
        cls.tomorrow = cls.today + timedelta(days=1)

        cls.customer = CustomerFactory(
            first_delivery_date=cls.today - timedelta(days=1),
            meal_assignment_paused=False,
        )

    def test_move_dishes_from_one_day_to_another(self):
        """We move some dishes from tomorrow to next day"""

        # generate one item only for tomorrow
        items = [{
            'date': dateformat.format(self.tomorrow, "Y-m-d"),
            'type': 'breakfast',
        }]

        view = CalendarScheduledMealsView()
        count_updated = view._save_scheduled_meals(
            customer_id=self.customer.id,
            date_from=self.today,
            date_to=self.tomorrow,
            items=items,
        )

        self.assertEqual(count_updated, 2)

        after_today = DailySchedule.objects.filter(
            customer=self.customer,
            date=self.today,
        ).values_list('breakfasts', 'lunches').first()

        after_tomorrow = DailySchedule.objects.filter(
            customer=self.customer,
            date=self.tomorrow,
        ).values_list('breakfasts', 'lunches').first()

        self.assertTupleEqual(after_today, (0, 0))
        self.assertTupleEqual(after_tomorrow, (1, 0))
