from datetime import date
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from apps.macroplate.factories import CustomerFactory

from ..api.serializers import CustomerSerializer
from ..models import Customer

RIGHT_NOW = timezone.now().replace(
    year=2021,
    month=1,
    day=13,
    hour=11,
    minute=19,
)


def right_now():
    return RIGHT_NOW


class TestCustomerHistory(TestCase):
    """Tests for Customers history feature."""

    @classmethod
    def setUpTestData(cls):
        cls.api_data = {
            'external_id': 6203,
            'first_name': 'John',
            'last_name': 'Lopez',
            'email': 'jlopez.iiv@gmail.com',
            'phone_number': '7148143159',
            'address': '10571 potter circle',
            'suite': '',
            'city': 'Villa park',
            'zip': 92861,
            'first_delivery_date': '2020-11-09',
            'delivery_notes': '',
            'delivery_window': '',
            'plan_type': {'id': 'paleo', 'name': 'Paleo'},
            'snacks_count': 1,
            'juice_count': 0,
            'juice_requested': 'no',
            'coffee_count': 0,
            'preferences': [
                {'name': 'all_dairy'},
                {'name': 'cheese'},
                {'name': 'yogurt'},
                {'name': 'all_seafood'},
                {'name': 'cod'},
                {'name': 'halibut'},
                {'name': 'mahi_mahi'},
                {'name': 'salmon'},
                {'name': 'tuna'},
                {'name': 'shrimp'},
                {'name': 'tilapia'},
                {'name': 'turkey_bacon'},
                {'name': 'okra'},
            ],
            'meal_assignment_paused': True,
            'promo_code': 'cristina377',
            'preferences_notes': 'No wild mushroom omelette',
            'carbs': '',
            'protein': '',
            'fat': '',
            'customized_days': {
                "monday": {
                    "delivery": 1,
                    "lunch": 2,
                    "breakfast": 1,
                },
                "tuesday": {
                    "delivery": 1,
                    "lunch": 2,
                    "breakfast": 1,
                },
                "wednesday": {
                    "delivery": 1,
                    "lunch": 2,
                    "breakfast": 1,
                },
            },
        }

    @mock.patch('django.utils.timezone.now', right_now)
    def test_serialize_and_save_new(self):
        """Test for catching errors with historical data for new Customer."""
        serializer = CustomerSerializer(data=self.api_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        customers = Customer.objects.all()

        self.assertEqual(customers.count(), 1)

    @mock.patch('django.utils.timezone.now', right_now)
    def test_serialize_and_save_existent(self):
        """Test for catching errors with historical data for existent Customer.
        """
        customer = CustomerFactory(
            external_id=self.api_data['external_id'],
            first_delivery_date=date(year=2020, month=11, day=19),
        )

        serializer = CustomerSerializer(customer, data=self.api_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        customers = Customer.objects.all()

        self.assertEqual(customers.count(), 2)

        # No historical data added when sending same data two times
        serializer = CustomerSerializer(customer, data=self.api_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        customers = Customer.objects.all()

        self.assertEqual(customers.count(), 2)

    def test_serialize_and_save_existent_with_timestamp(self):
        """Test for catching errors with historical data for existent Customer.

        Check case when receiving "timestamp" field.
        The "timestamp" denotes when a user edited Customer data on the device.

        """
        customer = CustomerFactory(
            external_id=self.api_data['external_id'],
            first_delivery_date=date(year=2020, month=11, day=19),
        )

        api_data_with_timestamp = self.api_data.copy()
        api_data_with_timestamp.update({
            'timestamp': right_now().timestamp()
        })

        serializer = CustomerSerializer(customer, data=api_data_with_timestamp)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        customers = Customer.objects.all()

        self.assertEqual(customers.count(), 2)

        # No historical data added when sending same data two times
        serializer = CustomerSerializer(customer, data=self.api_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        customers = Customer.objects.all()

        self.assertEqual(customers.count(), 2)

    def test_meal_assignment_paused_applied_properly(self):
        """Test for "meal_assignment_paused" applied properly.

        It should not change for

        """
        meal_assignment_paused = False

        customer = CustomerFactory(
            external_id=self.api_data['external_id'],
            first_delivery_date=date(year=2020, month=11, day=19),
            meal_assignment_paused=meal_assignment_paused,
        )

        api_data_with_timestamp = self.api_data.copy()
        api_data_with_timestamp.update({
            'timestamp': right_now().timestamp(),
            'meal_assignment_paused': not meal_assignment_paused,
        })

        serializer = CustomerSerializer(customer, data=api_data_with_timestamp)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        customer.refresh_from_db()
        # Meal assignment changed for actual customer data
        self.assertNotEqual(customer.meal_assignment_paused, meal_assignment_paused)  # noqa

        new_customer_data = customer.history.first()

        # Historical data for the customer created
        # with old "meal_assignment_paused" value
        self.assertEqual(new_customer_data.meal_assignment_paused, meal_assignment_paused)  # noqa
