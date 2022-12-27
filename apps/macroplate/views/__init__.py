from .assigned_menus import (
    AssignedMenuEditView,
    AssignedMenuSelectDayView,
    AssignedMenuSelectView,
)
from .customer_notes import CustomerNoteCreateView
from .customers import (
    CustomerCreateView,
    CustomerDeleteView,
    CustomerDetailView,
    CustomerImportView,
    CustomerListView,
    CustomerUpdateView,
)
from .daily_menus import (
    DailyMenuEditView,
    DailyMenuSaveView,
    DailyMenuSelectView,
)
from .daily_schedule import DailyScheduleSelectView, DailyScheduleView
from .dashboard import DashboardSelectView, DashboardView
from .ingredients import (
    IngredientCreateView,
    IngredientDeleteView,
    IngredientListView,
    IngredientUpdateView,
)
from .meals import (
    MealCreateView,
    MealDeleteView,
    MealDetailView,
    MealListView,
    MealUpdateView,
)
from .plan_type import (
    PlanTypeCreateView,
    PlanTypeDeleteView,
    PlanTypeListView,
    PlanTypeUpdateView,
)
from .preferences import (
    PreferenceCreateView,
    PreferenceDeleteView,
    PreferenceListView,
    PreferenceUpdateView,
)
