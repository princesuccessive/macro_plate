import math
from datetime import date
from typing import Iterable, List, NamedTuple, Set, Tuple

from django.db.models import Prefetch

from celery.exceptions import InvalidTaskError

from apps.celery.utils import update_task_progress
from apps.macroplate.models import (
    AssignedMeal,
    AssignedMealType,
    AssignedMenu,
    Customer,
    DailyMenu,
    DailySchedule,
    Ingredient,
    Meal,
    MealIngredient,
    MealModifier,
)

from .schedule_service import create_schedules_for_day


class MealAndMods(NamedTuple):
    """Named tuple to store meal-mods pairs for customers' meals."""
    meal: Meal
    mods: Set[MealModifier]


def assign_meals(current_date: date) -> Tuple[int, int]:
    """Assign meals for all customer in current day."""
    total, issues = 0, 0

    create_schedules_for_day(date=current_date)

    daily_schedules = DailySchedule.objects.filter(
        date=current_date,
        has_delivery=True,
    ).select_related(
        'customer',
    ).prefetch_related(
        'customer__preferences',
    )

    try:
        current_menu: DailyMenu = DailyMenu.objects.get(date=current_date)
    except DailyMenu.DoesNotExist:
        raise InvalidTaskError(f"Daily menu for {current_date} not found")

    # All available meals for current plan_type
    mods_qs = MealModifier.objects.select_related('ingredient_from')
    ingredients_qs = MealIngredient.objects.select_related(
        'ingredient',
    ).prefetch_related('ingredient__preferences')

    meals = current_menu.meals.select_related(
        'plan_type',
    ).prefetch_related(
        Prefetch('mods', queryset=mods_qs),
        Prefetch('ingredients', queryset=ingredients_qs),
    ).order_by('dailymenuitem__order')

    total = daily_schedules.count()
    for num, daily_schedule in enumerate(daily_schedules.all(), 1):
        assigned_menu: AssignedMenu = create_and_fill_assigned_menu(
            daily_schedule=daily_schedule,
            daily_menu=current_menu,
            meals=meals,
        )

        if assigned_menu.has_issues:
            issues += 1

        update_task_progress(total, num, issues=issues)
    return total, issues


def create_and_fill_assigned_menu(
    daily_schedule: DailySchedule,
    daily_menu: DailyMenu,
    meals: Iterable[Meal],
) -> AssignedMenu:
    """Create an assigned menu for a given daily schedule and fill it.

    First, we create or get and reset an assigned menu.
    Then from the list of meals, we pick available - remove meals excluded
    by customer, and prioritize preferred meals.

    Then we go over the meals again, this time removing meals which have
    ingredients, disliked by the customer. If disliked ingredients
    have modifiers (remove or substitute), we add them with a list of
    modifiers.

    From the resulting meals list, we create a bulk of AssignedMeal objects.
    """
    customer: Customer = daily_schedule.customer
    assigned_menu: AssignedMenu = AssignedMenu.get_reset_or_create(
        customer=customer,
        daily_menu=daily_menu,
    )
    available_meals: List[Meal] = get_available_meals_for_customer(
        customer=customer,
        meals=meals,
    )
    meals: List[MealAndMods]
    has_issues: bool

    meals, has_issues = filter_suitable_meals(
        customer=customer,
        available_meals=available_meals,
        breakfasts_count=daily_schedule.breakfasts,
        lunches_count=daily_schedule.lunches,
    )

    assigned_meals = []
    for meal, mods in meals:
        if meal.breakfast:
            meal_type = AssignedMealType.BREAKFAST
        else:
            meal_type = AssignedMealType.LUNCH

        assigned_meals.append(AssignedMeal(
            meal=meal,
            mods=', '.join(map(str, mods)),
            assigned_menu=assigned_menu,
            meal_type=meal_type,
        ))

    AssignedMeal.objects.bulk_create(assigned_meals)
    assigned_menu.has_issues = has_issues
    assigned_menu.save()
    return assigned_menu


def filter_suitable_meals(
    customer: Customer,
    available_meals: List[Meal],
    breakfasts_count: int,
    lunches_count: int,
) -> Tuple[List[MealAndMods], bool]:
    """Filter available meals into a list of suitable meals for the customer.

    For each available meal, check ingredient preferences, if check is passed -
    add a meal to a list of breakfast/lunch meals, until the required count
    is reached.

    A meal might pass the check, but require hard modifiers,
    so we give such meals less priority.

    If there are not enough meals, we return the `has_issues=True` flag,
    and try to fill with duplicates of existing meals if any were added.
    """
    breakfasts: List[MealAndMods] = []
    breakfasts_with_mods: List[MealAndMods] = []
    lunches: List[MealAndMods] = []
    lunches_with_mods: List[MealAndMods] = []

    def has_enough_breakfasts() -> bool:
        return len(breakfasts) >= breakfasts_count

    def has_enough_lunches() -> bool:
        return len(lunches) >= lunches_count

    for meal in available_meals:
        if has_enough_breakfasts() and has_enough_lunches():
            break

        match: bool
        mods: Set[MealModifier]
        match, mods = check_meal_match_to_customer(
            customer=customer,
            meal=meal,
        )
        if not match:
            continue

        meal_and_mods = MealAndMods(meal, mods)

        if any(mod.is_hard for mod in mods):
            if meal.breakfast:
                breakfasts_with_mods.append(meal_and_mods)
            else:
                lunches_with_mods.append(meal_and_mods)

        elif meal.breakfast and not has_enough_breakfasts():
            breakfasts.append(meal_and_mods)
        elif meal.regular and not has_enough_lunches():
            lunches.append(meal_and_mods)

    breakfasts += breakfasts_with_mods
    lunches += lunches_with_mods

    has_issues = False

    if not has_enough_breakfasts() or not has_enough_lunches():
        has_issues = True

        if breakfasts and breakfasts_count:
            breakfasts *= math.ceil(breakfasts_count / len(breakfasts))
        if lunches and lunches_count:
            lunches *= math.ceil(lunches_count / len(lunches))

    meals = breakfasts[:breakfasts_count] + lunches[:lunches_count]
    return meals, has_issues


def get_available_meals_for_customer(
    customer: Customer,
    meals: list,
) -> List[Meal]:
    """Filter meals available for customer.

    Remove excluded meals, and meals for a plan type different
    from the customer's.
    Then move preferred meals to the start of the list.
    """
    excluded_meals = set(customer.excluded_meals.all())
    preferred_meals = set(customer.preferred_meals.all())

    available_meals = [
        meal for meal in meals
        if (
            meal.plan_type_id == customer.plan_type_id and
            meal not in excluded_meals
        )
    ]

    available_meals.sort(
        key=lambda meal: meal not in preferred_meals,
    )
    return available_meals


def check_meal_match_to_customer(
    customer: Customer,
    meal: Meal,
) -> Tuple[bool, Set[MealModifier]]:
    """Check that meal is OK for customer.

    According to business logic, first we have to check whether the meal
    is suitable for the customer.
    NOTE: customer's "preferences" are actually dislikes. If the meal
    contains any of these dislikes, we try to substitute with modifiers.

    If in the end the dish is suitable for the user, return:
    * first element: `True` the first element,
    * second element: set of necessary modifications (it can be empty).

    If the dish is not suitable, return (False, [])
    """
    if not customer.preferences.exists():
        return True, set()

    customer_dislikes = set(customer.preferences.all())
    mods = set()

    for meal_ingredient in meal.ingredients.all():
        ingredient: Ingredient = meal_ingredient.ingredient
        ingredient_prefs = set(ingredient.preferences.all())

        intersection = customer_dislikes & ingredient_prefs
        if not intersection:
            continue
        # meal.mods is prefetched, so we don't use DB filter
        mods_for_ingredient: List[MealModifier] = [
            mod for mod in meal.mods.all()
            if mod.ingredient_from == ingredient
        ]

        if not mods_for_ingredient:
            return False, set()

        mods.add(mods_for_ingredient[0])
    return True, mods
