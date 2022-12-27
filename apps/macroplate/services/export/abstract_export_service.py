import abc


class AbstractExportService(metaclass=abc.ABCMeta):
    """Abstract class for export service"""
    # count of all exported items
    total = 0

    @abc.abstractmethod
    def export(self, export_format=None):
        """Export prepared data in specific format."""
