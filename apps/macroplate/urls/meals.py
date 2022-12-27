from django.urls import path

from apps.macroplate import views
from apps.macroplate.views.meals_import_export import MealsImportExportView

urlpatterns = [
    path(
        'meal/',
        views.MealListView.as_view(),
        name='meal-list',
    ),
    path(
        'meal/add/',
        views.MealCreateView.as_view(),
        name='meal-add',
    ),
    path(
        'meal/<int:pk>/',
        views.MealDetailView.as_view(),
        name='meal-detail',
    ),
    path(
        'meal/<int:pk>/update/',
        views.MealUpdateView.as_view(),
        name='meal-update',
    ),
    path(
        'meal/<int:pk>/delete/',
        views.MealDeleteView.as_view(),
        name='meal-delete',
    ),
    path(
        'meal/import-export/',
        MealsImportExportView.as_view(),
        name='meals-import-export',
    ),
]
