from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FakeAppConfig(AppConfig):
    """Config for fake application.

    Attributes:
        app_urls (str): path to module with application urls, for example:
            'apps.utils.custom_fields.tests.my_fake_app.urls'
        api_urls (str): path to module with aplication API urls, for example:
            'apps.utils.custom_fields.tests.my_fake_app.api.urls'

    Examples:
        from libs.apps import FakeAppConfig


        class CustomFieldsFakeAppConfig(FakeAppConfig):
            api_urls = 'apps.utils.custom_fields.tests.' \
                       'custom_fields_fake_app.api.urls'
            name = 'apps.utils.custom_fields.tests.custom_fields_fake_app'
    """

    app_urls = None
    api_urls = None


def is_fake_app(app_config):
    """Check whether app_config is related to fake app.

    Args:
        app_config (AppConfig): instance of application config to check

    Returns:
        bool: True if application is fake
    """
    return isinstance(app_config, FakeAppConfig)


class LibsAppConfig(AppConfig):
    """Config to execute some code when app config loads."""

    name = 'libs'
    verbose_name = _('Libs')
