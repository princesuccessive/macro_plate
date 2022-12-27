from django.urls import path, register_converter

from apps.core import converters
from apps.macroplate import views

register_converter(converters.DateConverter, 'date')

urlpatterns = [
    path(
        'assigned-menus/',
        views.AssignedMenuSelectDayView.as_view(),
        name='assigned-menus-select-day',
    ),
    path(
        'assigned-menus/<date:date>/',
        views.AssignedMenuSelectView.as_view(),
        name='assigned-menus',
    ),
    path(
        'assigned-menus/<date:date>/<int:customer_id>/',
        views.AssignedMenuEditView.as_view(),
        name='assigned-menus-edit',
    ),
]
