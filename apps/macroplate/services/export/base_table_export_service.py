import tablib

from apps.celery.utils import update_task_progress
from apps.macroplate.services.export import AbstractExportService


class BaseTableExportService(AbstractExportService):
    """Base service for exports.

    For each column in columns you can define getter for value like this:
    >>> def get_full_name(row_data):
    >>>     return rows_data.first_name + ' ' + rows_data.last_name
    and it will be automatically used.

    In `columns` you must define all column in format:
        - key: name of field (property of row_data)
        - value: name of column in exported table
    """
    total = 0
    columns = dict()
    # Need report export progress in celery task, or not.
    report_progress = True

    def __init__(self):
        """Initiate the service."""
        self.data = tablib.Dataset()

    @staticmethod
    def default_getter(row_data, field: str):
        """By default, get attribute of data."""
        value = getattr(row_data, field)

        if not value or value == '0':
            return None
        return value

    def rows_data(self) -> list:
        """Get data for rows."""
        return []

    def process_data(self, rows_data):
        """Prepare data for the export."""
        rows = []
        self.total = len(rows_data)
        for num, data in enumerate(rows_data, 1):
            # if row is none, add empty line
            if data is None:
                rows.append(self.empty_row)
                continue

            row = {}
            for column in self.columns.keys():
                getter = getattr(self, f'get_{column}', None)

                if getter:
                    value = getter(data)
                else:
                    value = self.default_getter(data, column)

                row[column] = value
            rows.append(row)

            if self.report_progress:
                update_task_progress(self.total, num)

        self.data.dict = rows
        self.data.headers = self.columns.values()

    def before_process_data(self, rows_data):
        """Do something before process the data"""
        pass

    def after_process_data(self, rows_data):
        """Do something after process the data"""
        pass

    def export(self, export_format='csv') -> str:
        """Export prepared data in specific format."""
        rows_data = self.rows_data()

        self.before_process_data(rows_data)
        self.process_data(rows_data)
        self.after_process_data(rows_data)

        return self.data.export(export_format)

    @property
    def empty_row(self):
        """Get empty row for this table."""
        return dict.fromkeys(self.columns.keys())
