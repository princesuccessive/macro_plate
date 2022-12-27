from django.db.models import QuerySet

from apps.macroplate.models import Preference

from .base_table_export_service import BaseTableExportService


class AllPreferencesExportService(BaseTableExportService):
    """Service to export Preferences."""

    report_progress = False
    columns = dict(
        id='ID',
        name='Name',
    )

    def rows_data(self) -> QuerySet:
        """Get all preferences."""
        return Preference.objects.all()
