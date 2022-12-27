import csv
import json
import logging
import re
from collections import defaultdict
from contextlib import suppress
from datetime import datetime
from functools import lru_cache
from typing import IO

from django.db import IntegrityError
from django.db.models.signals import post_save
from django.utils import timezone

from apps.core.utils import clear_string, get_week_start
from apps.macroplate.api.serializers import CustomerSerializer
from apps.macroplate.models import Customer, PlanType, Preference
from apps.macroplate.models.customers import CustomerPreference

logger = logging.getLogger('django')

# List of predefined Plans, which will be created before import
PREDEFINED_PLANS = {
    'slim': 'Slim',
    'trad': 'Trad',
    'high-pro': 'High-pro',
    'paleo': 'Paleo',
    'custom': 'Custom',
    'keto': 'Keto',
    'weightloss': 'Weightloss',
    'veg': 'Veg',
    'vegan': 'Vegan',
    'hcg-p-update-2': 'HCG phase 2',
    'hcg-update-stable': 'HCG Stabilization',
    'hcg-p2': 'HCG',
}


def create_predefined_plans(plans_dict):
    # create predefined plans
    for plan_id, plan_name in plans_dict.items():
        PlanType.objects.get_or_create(id=plan_id, defaults={
            'name': plan_name
        })


def allergies_to_prefs(allergies: str):
    """Convert string with allergies to list of preferences names."""
    if not allergies:
        return []

    return [{"name": pref.strip()} for pref in allergies.split(",")]


def parse_fd_date(date: str):
    """Parse first_delivery_date from string or set default value."""
    if not date:
        return get_week_start(timezone.now().date())

    with suppress(ValueError):
        return datetime.strptime(date, '%Y-%m-%d').date()

    with suppress(ValueError):
        return datetime.strptime(date, '%m/%d/%y').date()

    with suppress(ValueError):
        return datetime.strptime(date, '%m/%d/%Y').date()


def snacks(data: str) -> int:
    """Get snacks count from string."""
    if not data or data == 'no':
        return 0
    parts = data.split('-')
    if len(parts) == 3:
        return int(data.split('-')[-2])
    if len(parts) == 2:
        return int(data.split('-')[-1])


def juice(data: str) -> int:
    if not data or data == 'no':
        return 0
    return int(data.split('-')[-1])


def coffee(data: str) -> int:
    if not data:
        return 0
    return int(data)


def dishes(data: str) -> int:
    if not data:
        return 0
    value = int(data)
    return value


@lru_cache(maxsize=None)
def parse_plan_id(stripe_plan: str) -> str:
    """Try to find plan ID in plan name"""
    if not stripe_plan:
        return ''

    patterns = [
        r'v\d-(.*?)-[\dx]-[\dx]',
        r'v\d-(.*?)-[\dx]',
        r'v\d-(.*?)',
        r'(.*?)-[\dx]-[\dx]',
        r'(.*?)-[\dx]',
        r'^(.*?)$',
    ]

    for pattern in patterns:
        m = re.search(pattern, stripe_plan)
        if not m:
            continue
        groups = m.groups()
        if groups[0]:
            return groups[0]

    return ''


def get_plan_type_id(row: dict) -> str:
    if 'plan_type' in row:
        return json.loads(row['plan_type'])['id']
    return parse_plan_id(row['stripe_plan'])


def get_preferences(row: dict) -> list:
    if 'preferences' in row:
        return json.loads(row['preferences'])
    return allergies_to_prefs(row['allergies'])


def get_boolean_value(row: dict, header) -> bool:
    if header not in row:
        return False
    res = {
        'no': False,
        'yes': True,
        'false': False,
        'true': True,
    }
    return res[row[header]]


def import_customers(csv_file: IO, clear_customers: bool = False):
    """Import customers from csv-file."""
    imported_count = 0
    errors_count = 0

    decoded_file = csv_file.read().decode('utf-8').splitlines()
    reader = csv.DictReader(decoded_file, delimiter=',')

    @lru_cache(maxsize=None)
    def get_plan(plan_id):
        return PlanType.objects.filter(id=plan_id).first()

    @lru_cache(maxsize=None)
    def get_or_create_preference(preference_name):
        pref_id = clear_string(preference_name).replace(' ', '-').lower()
        try:
            obj, _ = Preference.objects.get_or_create(name=preference_name)
        except IntegrityError:
            obj, _ = Preference.objects.get_or_create(id=pref_id, defaults={
                'name': preference_name,
            })
        return obj

    customers_to_create = []
    customer_preferences = {}
    warnings = defaultdict(list)
    not_imported_rows = defaultdict(list)

    logger.info('Processing CSV file...')

    existent_customers = set(
        Customer.objects.all().values_list('external_id', flat=True)  # noqa
    )

    for row in reader:
        if not clear_customers and row['external_id'] in existent_customers:
            external_id = row['external_id']
            logger.info(f'Customer with External Id {external_id} exists')
            continue

        key = (row['external_id'], row['first_name'], row['last_name'])

        payload = dict(
            external_id=row['external_id'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            email=row['email'],
            phone_number=row['phone_number'],
            address=row['address'],
            suite=row['suite'],
            city=row['city'],
            zip=row['zip'],
            first_delivery_date=parse_fd_date(row['first_delivery_date']),
            delivery_notes=row['delivery_notes'][:350],
            delivery_window='',
            plan_type=dict(id=get_plan_type_id(row)),
            snacks_count=snacks(row['snacks_count']) or 0,
            juice_count=juice(row['juice_count']),
            juice_requested='yes' if get_boolean_value(row, 'juice_requested') else 'no',  # noqa
            coffee_count=coffee(row['coffee_count']),
            preferences=get_preferences(row),
            preferences_notes=row['preferences_notes'][:500],
            meal_assignment_paused=get_boolean_value(row, 'meal_assignment_paused'),  # noqa
            promo_code=row['promo_code'],
            carbs=row['carbs'],
            protein=row['protein'],
            fat=row['fat'],
        )

        # correct errors

        for field in ['first_name', 'last_name', 'phone_number']:
            if not payload[field]:
                payload[field] = "BLANK"
                warnings[key].append(f'Empty {field} field')

        if not payload['email']:
            payload['email'] = "BLANK@example.com"
            warnings[key].append('Empty email')

        if not get_plan(payload['plan_type']['id']):
            not_imported_rows[key].append(
                f'Plan with id "{payload["plan_type"]["id"]}" not found in '
                f'the system'
            )
            errors_count += 1
            continue

        # serializer payload and check that it's valid
        serializer = CustomerSerializer(data=payload)
        if not serializer.is_valid():
            logger.info(f"invalid: {serializer.errors}")
            errors_count += 1
            not_imported_rows[key].append(str(serializer.errors))
            continue

        # Create plan type and set it to customer
        params = serializer.validated_data
        plan = params.pop('plan_type')
        params['plan_type'] = get_plan(plan['id'])

        # Create preferences and save it for future
        preferences = [
            get_or_create_preference(pref['name'])
            for pref in params.pop('preferences')
        ]

        # Create Customer without saving.
        customer = Customer(**params)
        customers_to_create.append(customer)

        # Save customer preferences for future
        customer_preferences[customer.external_id] = preferences

        imported_count += 1

    if clear_customers:
        logger.info('Clear DB')
        Customer.objects.all().delete()
        create_predefined_plans(PREDEFINED_PLANS)

    logger.info('Bulk create customers')
    Customer.objects.bulk_create(
        customers_to_create,
        ignore_conflicts=True,
    )

    # Send post_save signals to create default weekly and daily schedules
    logger.info('Create defaults')
    for customer in Customer.objects.all().filter(
        external_id__in=[c.external_id for c in customers_to_create],
    ):
        post_save.send(sender=Customer, instance=customer, created=True)

    logger.info('Create customer preferences')
    customer_preferences_to_create = []
    for customer in Customer.objects.all():
        if customer.external_id not in customer_preferences:
            continue
        customer_preferences_to_create.extend([
            CustomerPreference(
                customer=customer,
                preference=pref,
                from_api=True,
            ) for pref in customer_preferences[customer.external_id]
        ])

    logger.info('Bulk create customer preferences')
    CustomerPreference.objects.bulk_create(
        customer_preferences_to_create,
        ignore_conflicts=True,
    )

    logger.info('Finish')

    return {
        'imported': imported_count,
        'errors': errors_count,
        'all': imported_count + errors_count,
        'not_imported': not_imported_rows,
        'warnings': warnings,
    }
