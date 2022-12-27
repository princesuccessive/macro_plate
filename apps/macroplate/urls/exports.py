from django.urls import path

from apps.macroplate import views

urlpatterns = [
    path(
        'exports/delivery/',
        views.DeliveryExportView.as_view(),
        name='exports-delivery',
    ),
    path(
        'exports/packaging/',
        views.PackagingExportView.as_view(),
        name='exports-packaging',
    ),
    path(
        'exports/mod-sheet/',
        views.ModSheetExportView.as_view(),
        name='exports-mod-sheet',
    ),
    path(
        'exports/promo-codes/',
        views.PromoCodesExportView.as_view(),
        name='exports-promo-codes',
    ),
    path(
        'exports/meal-cards/',
        views.MealCardsExportView.as_view(),
        name='exports-meal-cards',
    ),
    path(
        'exports/meal-quantity/',
        views.MealQuantityExportView.as_view(),
        name='exports-meal-quantity',
    ),
]
