from django.urls import path

from apps.macroplate import views

urlpatterns = [
    path(
        'plan-types/',
        views.PlanTypeListView.as_view(),
        name='plan-type-list',
    ),
    path(
        'plan-types/add/',
        views.PlanTypeCreateView.as_view(),
        name='plan-type-add',
    ),
    path(
        'plan-types/<str:pk>/update/',
        views.PlanTypeUpdateView.as_view(),
        name='plan-type-update',
    ),
    path(
        'plan-types/<str:pk>/delete/',
        views.PlanTypeDeleteView.as_view(),
        name='plan-type-delete',
    ),
]
