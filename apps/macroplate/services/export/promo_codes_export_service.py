from django.db.models.query import QuerySet

from apps.core.utils import get_week_start
from apps.macroplate.models import Customer
from apps.macroplate.services.export import (
    BaseTableExportService,
    ByDateExportServiceMixin,
)


class PromoCodesExportService(
    ByDateExportServiceMixin,
    BaseTableExportService,
):
    """Service to export Promo codes."""

    columns = dict(
        promo_code='Code',
    )

    def rows_data(self) -> QuerySet:
        """Get customers information and remove customers without dishes."""

        start_week = get_week_start(self.export_date)

        qs = Customer.objects.for_delivery(self.export_date).filter(
            first_delivery_date=start_week,
        ).exclude(
            promo_code='',
        ).has_dishes_for_date(
            date=self.export_date,
        ).exclude(
            # remove customers who already get meals on this week
            assignedmenu__daily_menu__date__lt=self.export_date,
            assignedmenu__assigned_meals__isnull=False,
        )
        return qs
