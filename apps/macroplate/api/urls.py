from django.urls import path

from .views import CustomerUpdateView

urlpatterns = [
    path(
        'customers',
        CustomerUpdateView.as_view(),
        name='api-customer',
    ),
]
