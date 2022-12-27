from django.urls import path

from .views import CalendarAssignedMealsView, CalendarScheduledMealsView

urlpatterns = [
    path(
        'assigned',
        CalendarAssignedMealsView.as_view(),
        name='api-calendar-assigned-meals',
    ),
    path(
        'scheduled',
        CalendarScheduledMealsView.as_view(),
        name='api-calendar-scheduled-meals',
    ),
]
