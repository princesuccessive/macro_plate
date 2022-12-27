from django.urls import path

from apps.macroplate import views

urlpatterns = [
    path(
        'preferences/',
        views.PreferenceListView.as_view(),
        name='preference-list',
    ),
    path(
        'preferences/add/',
        views.PreferenceCreateView.as_view(),
        name='preference-add',
    ),
    path(
        'preferences/<str:pk>/update/',
        views.PreferenceUpdateView.as_view(),
        name='preference-update',
    ),
    path(
        'preferences/<str:pk>/delete/',
        views.PreferenceDeleteView.as_view(),
        name='preference-delete',
    ),
]
