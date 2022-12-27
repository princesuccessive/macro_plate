from datetime import date, datetime

from django.conf import settings
from django.test import TestCase

import pytz

from apps.macroplate.factories import CustomerFactory
from apps.macroplate.models import Customer

client_tz = pytz.timezone(settings.CLIENT_TZ)

wed_11_59_am = client_tz.localize(
    datetime(year=2020, month=7, day=8, hour=11, minute=59)
)

wed_12_01_pm = client_tz.localize(
    datetime(year=2020, month=7, day=8, hour=12, minute=1)
)


class TestCustomerHistory(TestCase):
    """Tests for Customers history feature."""

    @classmethod
    def setUpTestData(cls):
        cls.sunday_12 = date(year=2020, month=7, day=12)
        cls.monday_13 = date(year=2020, month=7, day=13)
        cls.sunday_19 = date(year=2020, month=7, day=19)
        cls.monday_20 = date(year=2020, month=7, day=20)

        cls.customer = CustomerFactory(
            first_delivery_date=date(year=2020, month=1, day=1),
            meal_assignment_paused=False,
        )

    def setUp(self):
        """Refresh Customer instance by ID or External ID."""
        if self.customer.pk:
            self.customer.refresh_from_db()
        else:
            self.customer = Customer.objects.get(
                external_id=self.customer.external_id,
            )

    def test_history_created_before_wednesday_noon(self):
        """When Customer updated before 12:00pm July 8th (Wednesday),
        historical data created and is active until July 12th (Monday).

        Updated Customer available for meal assignment since July 13th (Monday)

        """
        self.customer.updated_at = wed_11_59_am
        self.customer.save()

        # Historical data created for the proper customer
        hist = Customer.objects.history().first()

        self.assertIsNotNone(hist)
        self.assertEqual(self.customer.id, hist.latest_id)

        # Last delivery date for historical Customer is Sunday, 12th
        self.assertEqual(hist.last_delivery_date, self.sunday_12)
        # First delivery date for updated Customer is Monday, 13th
        self.assertEqual(self.customer.first_delivery_date, self.monday_13)

    def test_history_created_after_wednesday_noon(self):
        """When Customer updated after 12:00pm July 8th (Wednesday),
        historical data created and is active until July 19th (Monday).

        Updated Customer available for meal assignment since July 20th (Monday)

        """
        self.customer.updated_at = wed_12_01_pm
        self.customer.save()

        # Historical data created
        hist = Customer.objects.history().first()
        self.assertIsNotNone(hist)

        # Last delivery date for historical Customer is Sunday, 19th
        self.assertEqual(hist.last_delivery_date, self.sunday_19)
        # First delivery date for updated Customer is Monday, 20th
        self.assertEqual(self.customer.first_delivery_date, self.monday_20)

    def test_history_not_created_twice(self):
        """Historical data not created twice if Customer updated before
        12pm Wednesday both times.

        """
        customer = CustomerFactory(
            first_delivery_date=date(year=2020, month=1, day=1),
            meal_assignment_paused=False,
        )

        customer.updated_at = wed_12_01_pm
        customer.save()
        customer.save()

        # Historical data created for the proper customer
        hist = Customer.objects.history()

        self.assertEqual(hist.count(), 1)

    def test_for_delivery(self):
        """Check `.for_delivery()` method returns historical data.

        1. edit customer before wed noon
        2. edit customer after wed noon
        3. call for_delivery before mon 13 - hist 1 should be returned
        4. call for_delivery between 13 and 20 - hist 2 should be returned
        5. call for_delivery after 20 - customer should be returned

        """
        self.customer.updated_at = wed_11_59_am
        self.customer.save()
        # Historical data for delivery before mon 13
        history_1 = Customer.objects.history().last()

        for_delivery = Customer.objects.for_delivery(self.sunday_12)

        self.assertEqual(for_delivery.count(), 1)
        self.assertEqual(for_delivery.last().id, history_1.id)

        self.customer.updated_at = wed_12_01_pm
        self.customer.save()
        # Historical data for delivery between 13 and 20
        history_2 = Customer.objects.history().last()

        for_delivery = Customer.objects.for_delivery(self.sunday_19)

        self.assertEqual(for_delivery.count(), 1)
        self.assertEqual(for_delivery.last().id, history_2.id)

        for_delivery = Customer.objects.for_delivery(self.monday_20).first()
        self.assertEqual(for_delivery.id, self.customer.id)

    def test_personal_info_updated_for_history(self):
        """Check personal info is updated in all historical after actual."""
        self.customer.updated_at = wed_12_01_pm
        new_address = self.customer.address + '1'
        self.customer.address = new_address
        self.customer.save()

        self.assertTrue(self.customer.history.exists())
        self.assertEqual(
            self.customer.history.count(),
            self.customer.history.filter(address=new_address).count(),
        )

    def test_history_deleted_for_single_customer(self):
        """Check historical data deleted when a single Customer deleted."""
        self.customer.save()

        # Historical data created
        self.assertTrue(Customer.objects.history().exists())

        self.customer.delete()
        # Historical data deleted
        self.assertFalse(Customer.objects.history().exists())
