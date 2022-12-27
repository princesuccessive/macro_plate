from django.views.generic import TemplateView

from apps.core.views import BaseView


class MealsImportExportView(TemplateView, BaseView):
    """Page to import/export meals, preferences and ingredients."""
    template_name = 'meals_import_export.html'
