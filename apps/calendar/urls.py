from django.urls import path

from apps.calendar.views import CustomerCalendarView

urlpatterns = [
    path(
        'customers/<int:customer_id>/calendar/',
        CustomerCalendarView.as_view(),
        name='customer-calendar',
    ),
]
