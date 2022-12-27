from datetime import datetime

from rest_framework import serializers

import pytz
from drf_writable_nested import (
    UniqueFieldsMixin,
    WritableNestedModelSerializer,
)

from apps.macroplate.models import (
    Customer,
    Ingredient,
    Meal,
    PlanType,
    Preference,
)
from apps.macroplate.models.customers import CustomerPreference
from apps.macroplate.models.daily_menu import DailyMenuItem
from apps.macroplate.services import create_or_update_defaults


class PlanTypeSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
    """Serializer for the `PlanType` model."""
    name = serializers.CharField(max_length=50, required=False)

    class Meta:
        model = PlanType
        fields = (
            'id',
            'name',
        )


class PreferenceSerializer(serializers.ModelSerializer):
    """Serializer for the `Preference` model."""

    class Meta:
        model = Preference
        fields = (
            'name',
        )


class TimeStampField(serializers.Field):
    """Field processing timestamps.

    Converts received timestamp into datetime to store in db and vice versa.
    Internal datetime is in the timezone that client uses.

    """

    def to_internal_value(self, timestamp: int) -> datetime:
        """Received timestamp -> internal datetime."""
        return datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.UTC)

    def to_representation(self, value: datetime) -> int:
        """Internal datetime -> timestamp."""
        return int(value.timestamp())


class CustomerScheduleDaySerializer(serializers.Serializer):
    """Serializer schedule data for one weekday."""
    delivery = serializers.BooleanField(source='has_delivery')
    breakfast = serializers.IntegerField(source='breakfasts')
    lunch = serializers.IntegerField(source='lunches')


class CustomerScheduleSerializer(serializers.Serializer):
    """Serializer for customized schedule for Customers."""
    monday = CustomerScheduleDaySerializer(required=False)
    tuesday = CustomerScheduleDaySerializer(required=False)
    wednesday = CustomerScheduleDaySerializer(required=False)
    thursday = CustomerScheduleDaySerializer(required=False)
    friday = CustomerScheduleDaySerializer(required=False)
    saturday = CustomerScheduleDaySerializer(required=False)
    sunday = CustomerScheduleDaySerializer(required=False)


class CustomerSerializer(WritableNestedModelSerializer):
    """Serializer for the `Customer` model."""
    external_id = serializers.CharField()
    plan_type = PlanTypeSerializer()
    preferences = PreferenceSerializer(many=True)
    plan_priority = serializers.CharField(required=False)
    timestamp = TimeStampField(source='updated_at', required=False)
    customized_days = CustomerScheduleSerializer(write_only=True)

    class Meta:
        model = Customer
        fields = (
            'external_id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'address',
            'suite',
            'city',
            'zip',
            'first_delivery_date',
            'delivery_notes',
            'delivery_window',
            'plan_type',
            'snacks_count',
            'juice_count',
            'juice_requested',
            'coffee_count',
            'preferences',
            'preferences_notes',
            'meal_assignment_paused',
            'promo_code',
            'carbs',
            'protein',
            'fat',
            'plan_priority',
            'timestamp',
            'customized_days',
        )

    def to_internal_value(self, data):
        """Modify external Id for Customer with `secondary` plan.

        This required to distinct Customer entities with primary and secondary
        plans and prevent overwriting of Customer data.

        """
        from ..models.customers import PlanPriority

        internal = super().to_internal_value(data)
        plan_priority = internal.get('plan_priority', PlanPriority.PRIMARY)

        if plan_priority == PlanPriority.SECONDARY:
            ext_id = f'{internal["external_id"]}-{PlanPriority.SECONDARY}'
            internal['external_id'] = ext_id

        return internal

    def create(self, validated_data: dict):
        """Add preferences and customized days after customer creation."""
        preferences = validated_data.pop('preferences', [])
        customized_days: dict = validated_data.pop('customized_days')

        instance: Customer = super().create(validated_data)
        self._create_preferences(preferences, instance)
        create_or_update_defaults(
            customer=instance,
            customized_days=customized_days,
        )

        return instance

    def update(self, instance: Customer, validated_data: dict):
        """Add preferences and customized days after customer update."""
        preferences = validated_data.pop('preferences', [])
        customized_days: dict = validated_data.pop('customized_days')

        instance: Customer = super().update(instance, validated_data)
        self._create_preferences(preferences, instance)
        create_or_update_defaults(
            customer=instance,
            customized_days=customized_days,
        )

        return instance

    def _create_preferences(self, preferences: list, customer: Customer):
        """Create preferences for the customer."""
        # clear all API preferences
        CustomerPreference.objects.filter(
            customer=customer,
            from_api=True,
        ).delete()

        # get all internal preferences
        internal_prefs = list(Preference.objects.filter(
            customerpreference__customer=customer,
            customerpreference__from_api=False,
        ))

        for preference in preferences:
            name = preference.get('name')

            # Preferences have unique names in case-insensitive terms
            existent_preferences = Preference.objects.filter(name__iexact=name)
            if existent_preferences.exists():
                preference = existent_preferences.first()
            else:
                preference = Preference(name=name)
                preference.save()  # call save to generate ID

            # if preference in internal list - skip this
            if preference in internal_prefs:
                continue

            # create the new preference for customer
            CustomerPreference.objects.create(
                customer=customer,
                preference=preference,
                from_api=True,
            )


class MealSerializer(serializers.ModelSerializer):
    """Serializer for the `Meal` model."""
    plan_type = PlanTypeSerializer()

    class Meta:
        model = Meal
        fields = (
            'id',
            'name',
            'breakfast',
            'plan_type',
        )


class DailyMenuItemSerializer(serializers.ModelSerializer):
    """Serializer for the `DailyMenuItem` model."""

    class Meta:
        model = DailyMenuItem
        fields = (
            'id',
            'meal_id',
            'order',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for the `Ingredient` model."""

    class Meta:
        model = Ingredient
        fields = (
            'quantity_type',
            'is_protein',
            'conversion_raw',
            'count',
        )
