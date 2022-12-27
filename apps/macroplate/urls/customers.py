from django.urls import path

from apps.macroplate import views

urlpatterns = [
    path(
        'customers/',
        views.CustomerListView.as_view(),
        name='customer-list',
    ),
    path(
        'customers/add/',
        views.CustomerCreateView.as_view(),
        name='customer-add',
    ),
    path(
        'customers/<int:pk>/',
        views.CustomerDetailView.as_view(),
        name='customer-detail',
    ),
    path(
        'customers/<int:pk>/update/',
        views.CustomerUpdateView.as_view(),
        name='customer-update',
    ),
    path(
        'customers/<int:pk>/delete/',
        views.CustomerDeleteView.as_view(),
        name='customer-delete',
    ),
    path(
        'customers/<int:customer_id>/add-note/',
        views.CustomerNoteCreateView.as_view(),
        name='customer-note-add',
    ),
    path(
        'customers/import/',
        views.CustomerImportView.as_view(),
        name='customer-import',
    ),
]
