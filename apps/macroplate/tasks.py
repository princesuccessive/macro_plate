import io
from typing import Type, Union
import zipfile

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from django.utils.dateparse import parse_date

from config.celery import app

from apps.celery.utils import update_task_progress
from apps.macroplate.models import Customer
from apps.macroplate.models.customers import CustomerQuerySet
from apps.macroplate.services import assign_meals as assign_meals_service
from apps.macroplate.services import export, import_all_meals_data


def get_current_timestamp() -> str:
    """Get current timestamp."""
    return timezone.now().strftime('%Y%m%d%H%M%S')


@app.task()
def assign_meals(date: str):
    """Assign meals for specific date."""
    date = parse_date(date)
    total, issues = assign_meals_service(date)

    return dict(
        total=total,
        done=total,
        issues=issues,
    )


def exporter(
    date: str,
    service_class: Union[
        Type[export.BaseTableExportService],
        Type[export.MealCardsExportService],
    ],
    file_path_template: str,
):
    """Run common logic of export tasks."""
    date = parse_date(date)

    file_path = file_path_template.format(
        export_date=date,
        time=get_current_timestamp(),
    )

    service = service_class(date)
    content = service.export()

    # if service returns string - convert it to bytes
    if not isinstance(content, bytes):
        content = content.encode('utf-8')

    saved_path = default_storage.save(file_path, ContentFile(content))
    url = default_storage.url(saved_path)

    return dict(
        total=service.total,
        done=service.total,
        file=url,
    )


@app.task()
def meal_cards_export(date: str):
    """Meal cards export."""
    return exporter(
        date,
        export.MealCardsExportService,
        'exports/{export_date}/meal_cards_{time}.pdf'
    )


@app.task()
def delivery_export(date: str):
    """Delivery document export."""
    return exporter(
        date,
        export.DeliveryDocumentExportService,
        'exports/{export_date}/delivery_{time}.csv'
    )


@app.task()
def packaging_export(date: str):
    """Packaging report export."""
    return exporter(
        date,
        export.PackagingReportExportService,
        'exports/{export_date}/packaging_{time}.csv'
    )


@app.task()
def mod_sheet_export(date: str):
    """Mod Sheet export."""
    return exporter(
        date,
        export.ModSheetExportService,
        'exports/{export_date}/mod_sheet_{time}.csv'
    )


@app.task()
def promo_codes_export(date: str):
    """Promo Codes export."""
    return exporter(
        date,
        export.PromoCodesExportService,
        'exports/{export_date}/promo_codes_{time}.csv'
    )


@app.task()
def meal_quantity_export(date: str):
    """Meal Quantity export."""
    return exporter(
        date,
        export.MealQuantityExportService,
        'exports/{export_date}/meal_quantity_{time}.csv'
    )


@app.task()
def remove_old_history_customers():
    """Delete old history customers."""
    customers: CustomerQuerySet = Customer.objects.all().filter(
        latest__isnull=False,
        last_delivery_date__lt=timezone.now()
    )

    return customers.delete()


@app.task()
def all_meal_data_export():
    """Export Preferences, Ingredients and meals in one zip archive."""
    zip_buffer = io.BytesIO()
    zip_file = zipfile.ZipFile(zip_buffer, 'w')

    exports = {
        'ingredients': export.AllIngredientsExportService,
        'meals': export.AllMealsExportService,
    }

    # Run exports one by one and push exported data to zip archive
    total, done = len(exports), 0
    update_task_progress(total, done)
    for name, export_class in exports.items():
        exporter_instance = export_class()
        content = exporter_instance.export()
        zip_file.writestr(f'{name}.csv', content)
        done += 1
        update_task_progress(total, done)

    zip_file.close()

    time = get_current_timestamp()
    file_path = f'exports/meals_{time}.zip'

    # Save in-memory file to default storage and return url
    saved_path = default_storage.save(file_path, zip_buffer)
    url = default_storage.url(saved_path)

    return dict(
        total=total,
        done=done,
        file=url,
    )


@app.task()
def all_meal_data_import(file_path: str):
    """Import Preferences, Ingredients and meals from one zip archive."""
    with default_storage.open(file_path) as file:
        zip_file = zipfile.ZipFile(file, 'r')

        # open preferences
        try:
            ingredients_file = zip_file.open('ingredients.csv', 'r')
            meals_file = zip_file.open('meals.csv', 'r')
        except KeyError as e:
            return dict(error=str(e))

        return import_all_meals_data(
            ingredients_file,
            meals_file,
        )
