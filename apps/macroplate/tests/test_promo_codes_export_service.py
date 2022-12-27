import datetime
from datetime import timedelta

from django.test import TestCase

from apps.macroplate.factories import (
    AssignedMenuWithMealsFactory,
    CustomerFactory,
    DailyMenuFactory,
)
from apps.macroplate.models import Customer
from apps.macroplate.services.export import PromoCodesExportService


class TestPromoCodesExportService(TestCase):
    """Test for `TestPromoCodesExportService`."""

    @classmethod
    def setUpTestData(cls):
        cls.monday = datetime.date(2019, 11, 25)
        cls.wednesday = cls.monday + timedelta(days=2)
        cls.friday = cls.monday + timedelta(days=4)

        cls.customer_past_week = CustomerFactory(
            first_delivery_date=cls.monday - timedelta(weeks=1),
        )
        cls.customer_monday = CustomerFactory(
            first_delivery_date=cls.monday,
        )
        cls.customer_wednesday = CustomerFactory(
            first_delivery_date=cls.monday,
        )

        # create menus for first two customers, for Monday
        cls.monday_daily_menu = DailyMenuFactory(date=cls.monday)
        for_delivery = Customer.objects.for_delivery(cls.monday)
        for customer in for_delivery:
            AssignedMenuWithMealsFactory(
                customer=customer,
                daily_menu=cls.monday_daily_menu,
            )

        # create menus for all customers, for Wednesday
        cls.wednesday_daily_menu = DailyMenuFactory(date=cls.wednesday)
        for_delivery = Customer.objects.for_delivery(cls.wednesday)
        for customer in for_delivery:
            AssignedMenuWithMealsFactory(
                customer=customer,
                daily_menu=cls.wednesday_daily_menu,
            )

    def test_no_past_week_in_promo_codes(self):
        """Check that old customer not shown in promo codes."""
        service = PromoCodesExportService(date=self.monday)
        customers = service.rows_data()
        self.assertEqual(customers.count(), 2)

    def test_none_promo_codes_for_friday(self):
        """In middle of week show only customer without meals from week-start.
        """
        service = PromoCodesExportService(date=self.friday)
        customers = service.rows_data()
        self.assertEqual(customers.count(), 0)
