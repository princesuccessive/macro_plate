from django.urls import path, register_converter

from apps.core import converters
from apps.macroplate import views

register_converter(converters.DateConverter, 'date')

urlpatterns = [
    path(
        '',
        views.DashboardSelectView.as_view(),
        name='dashboard-select',
    ),
    path(
        '<date:date>/',
        views.DashboardView.as_view(),
        name='dashboard',
    ),
]
