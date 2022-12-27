from . import (
    assigned_menus,
    customers,
    daily_menu,
    dashboard,
    ingredients,
    meals,
    plan_types,
    preferences,
    schedules,
)

urlpatterns = sum([
    ingredients.urlpatterns,
    preferences.urlpatterns,
    plan_types.urlpatterns,
    meals.urlpatterns,
    customers.urlpatterns,
    schedules.urlpatterns,
    daily_menu.urlpatterns,
    assigned_menus.urlpatterns,
    dashboard.urlpatterns,
], [])
