from io import BytesIO

from django.template.loader import get_template

from PyPDF2 import PdfFileMerger
from xhtml2pdf import pisa

from apps.celery.utils import update_task_progress
from apps.macroplate.models import AssignedMenu, Customer
from apps.macroplate.services.export import (
    AbstractExportService,
    ByDateExportServiceMixin,
)


class MealCardsExportService(ByDateExportServiceMixin, AbstractExportService):
    """Service to export Meal Cards."""

    filename = 'meal_cards_{rnd}.pdf'
    columns = dict(
        promo_code='Code',
    )

    def pages_data(self):
        """Get all assigned menus and create information for each card."""

        customers = Customer.objects.for_delivery(
            self.export_date,
        ).select_related(
            'plan_type'
        ).prefetch_related(
            'daily_schedules'
        ).has_dishes_for_date(self.export_date)

        menus = AssignedMenu.objects.filter(
            daily_menu__date=self.export_date,
        ).prefetch_related(
            'assigned_meals',
            'assigned_meals__meal',
            'assigned_meals__meal__mods',
            'customer__preferences',
        ).select_related(
            'customer',
            'customer__plan_type',
        ).order_by(
            'customer__plan_type',
            'customer__first_name',
            'customer__last_name',
        ).filter(
            customer__in=customers,
        )

        pages = []
        for num, menu in enumerate(menus, 1):
            customer: Customer = menu.customer
            data = dict(
                customer=customer,
                **menu.assigned_meals_by_types,
            )

            pages.append(data)
        return pages

    def export(self, export_format='pdf'):
        """Export prepared data in specific format."""
        # open output file for writing (truncated binary)

        template_path = 'exports/meal_card.html'

        pages = self.pages_data()
        self.total = len(pages)

        pdf_merger = PdfFileMerger()
        for num, page in enumerate(pages):
            template = get_template(template_path)
            html = template.render({'page': page})

            buffer = BytesIO()
            pisa.CreatePDF(
                html,
                dest=buffer,
            )
            pdf_merger.append(buffer)
            update_task_progress(self.total, num)

        buffer = BytesIO()
        pdf_merger.write(buffer)
        return buffer.getvalue()
