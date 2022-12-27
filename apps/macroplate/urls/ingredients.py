from django.urls import path

from apps.macroplate import views

urlpatterns = [
    path(
        'ingredients/',
        views.IngredientListView.as_view(),
        name='ingredient-list',
    ),
    path(
        'ingredients/add/',
        views.IngredientCreateView.as_view(),
        name='ingredient-add',
    ),
    path(
        'ingredients/<int:pk>/update/',
        views.IngredientUpdateView.as_view(),
        name='ingredient-update',
    ),
    path(
        'ingredients/<int:pk>/delete/',
        views.IngredientDeleteView.as_view(),
        name='ingredient-delete',
    ),
]
