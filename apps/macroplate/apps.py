from django.apps import AppConfig


class MacroPlateConfig(AppConfig):
    """Configuration for the `macroplate` app."""
    name = 'apps.macroplate'

    def ready(self):
        """Prepare application, connect signals."""
        from . import signals  # noqa
