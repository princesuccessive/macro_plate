from django.dispatch import receiver

from apps.macroplate.models import Customer, create_history
from apps.macroplate.services import customer_history_service


@receiver(create_history, sender=Customer)
def create_historical_data(sender, instance, *args, **kwargs):
    """Create historical data for a Customer."""
    customer_history_service.create_historical_data(instance)
