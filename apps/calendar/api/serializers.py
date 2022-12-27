from rest_framework import serializers

from apps.macroplate.models import AssignedMeal, AssignedMealType, Customer


class CalendarQueryParamsSerializer(serializers.Serializer):
    """Serializer for query params for calendar endpoints."""
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
    )
    start = serializers.DateField()
    end = serializers.DateField()
    today = serializers.DateField()

    class Meta:
        fields = [
            'customer_id',
            'start',
            'date',
            'today',
        ]


class AssignedMealForCalendarSerializer(serializers.ModelSerializer):
    """Info about the assigned meal for the calendar."""

    meal_name = serializers.CharField(source='meal.name')
    date = serializers.DateField(source='assigned_menu.daily_menu.date')

    class Meta:
        model = AssignedMeal
        fields = [
            'id',
            'meal_id',
            'meal_name',
            'date',
        ]


class SaveScheduleMealSerializer(serializers.Serializer):
    """Serializer for item in SaveScheduleSerializer.

    This item contain information about one scheduled meal for customer.
    """

    date = serializers.DateField()
    type = serializers.ChoiceField(
        choices=tuple(
            choice[0] for choice in AssignedMealType.CHOICES
        ),
    )


class SaveScheduleSerializer(serializers.Serializer):
    """Serializer for saving the user's schedule."""

    items = SaveScheduleMealSerializer(many=True)
    start = serializers.DateField()
    end = serializers.DateField()
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
    )
    today = serializers.DateField()

    class Meta:
        model = AssignedMeal
        fields = [
            'items',
            'start',
            'end',
            'today',
            'customer_id',
        ]
