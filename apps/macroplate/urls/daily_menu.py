from django.urls import path, register_converter

from apps.core import converters
from apps.macroplate import views

register_converter(converters.DateConverter, 'date')

urlpatterns = [
    path(
        'daily-menu/',
        views.DailyMenuSelectView.as_view(),
        name='daily-menu',
    ),
    path(
        'daily-menu/<date:date>/',
        views.DailyMenuEditView.as_view(),
        name='daily-menu-edit',
    ),
    path(
        'daily-menu/<date:date>/save/',
        views.DailyMenuSaveView.as_view(),
        name='daily-menu-save',
    ),
]
