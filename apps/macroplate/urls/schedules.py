from django.urls import path, register_converter

from apps.core import converters
from apps.macroplate import views

register_converter(converters.DateConverter, 'date')

urlpatterns = [
    path(
        'schedules/daily/default/',
        views.DailyScheduleSelectView.as_view(),
        name='schedules-daily-default-select',
    ),
    path(
        'schedules/daily/<int:customer_id>/<int:day_of_week>/default/',
        views.DailyScheduleView.as_view(),
        name='schedules-daily-default',
    ),
]
