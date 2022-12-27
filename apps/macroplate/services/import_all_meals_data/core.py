import csv
import logging
from typing import IO, Dict, List, Set

from django.db import IntegrityError, transaction

from rest_framework.exceptions import ErrorDetail, ValidationError

from apps.celery.utils import update_task_progress
from apps.core.utils import chunks, clear_string, is_yes
from apps.macroplate.models import (
    Ingredient,
    Meal,
    MealIngredient,
    MealModifier,
    PlanType,
    Preference,
)
from apps.macroplate.models.meal_modifiers import ModTypes
from apps.macroplate.models.preferences import generate_preference_id

from ...api.serializers import IngredientSerializer
from . import exceptions
from .structures import IngredientRow, MealIngredientRow, MealRow

logger = logging.getLogger('django')


def create_csv_reader(file: IO):
    """Create csv reader.

    Just read input stream, convert it from utf-8 (because export in utf-8
    format), and skip first line with headers.
    """
    decoded_file = file.read().decode('utf-8').splitlines()
    reader = csv.reader(decoded_file, delimiter=',')
    # skip first row
    next(reader, None)
    return reader


def get_new_preferences(
    raw_ingredients: List[IngredientRow],
    preferences_ids_map: Dict[str, Preference],
) -> List[Preference]:
    """Create list of new created preferences."""
    created_preferences: List[Preference] = []

    # Extract all preference names from
    preference_names: Set[str] = set()
    for row in raw_ingredients:
        ingredient_preference_names = row.preferences
        preference_names.update(ingredient_preference_names)

    preference_ids_to_create: Set[str] = set()
    for preference_name in preference_names:
        # skip empty preference
        if not preference_name:
            continue

        pref_id = generate_preference_id(preference_name)

        # skip exists preference
        if pref_id in preferences_ids_map:
            continue

        # skip preferences that we already created
        if pref_id in preference_ids_to_create:
            continue
        preference_ids_to_create.add(pref_id)

        preference, created = Preference.objects.get_or_create(
            id=pref_id,
            defaults=dict(
                name=preference_name,
                name_unique=clear_string(preference_name),
            )
        )

        created_preferences.append(preference)

    return created_preferences


def create_preferences_map(items: List[Preference]) -> Dict[str, Preference]:
    """Create map with preferences."""
    return {p.id: p for p in items}


def create_ingredients_map(items: List[Ingredient]) -> Dict[str, Ingredient]:
    """Create map with ingredients."""
    return {i.name: i for i in items}


def errors_to_string(errors: Dict[str, List[ErrorDetail]]) -> str:
    """Convert validation errors to string."""
    messages = []
    for field, field_errors in errors.items():
        messages.append(field + ' - ' + field_errors[0])
    return ', '.join(messages)


def validate_ingredient(row: IngredientRow):
    """Validate ingredient row."""
    ingredient_serializer = IngredientSerializer(
        data=dict(
            name=row.name,
            quantity_type=row.quantity_type,
            is_protein=is_yes(row.is_protein),
            conversion_raw=row.conversion_raw,
            count=is_yes(row.is_count),
        )
    )
    try:
        ingredient_serializer.is_valid(raise_exception=True)
    except ValidationError as e:
        errors = errors_to_string(e.detail)
        raise exceptions.InvalidDataException(
            f'Validation errors for ingredient "{row.name}": ' + errors
        )


def validate_decimal(value: str) -> float:
    """Validate decimal value."""
    try:
        return float(value)
    except ValueError:
        raise Exception('Should be decimal value')


def _create_all_meals_data(
    ingredient_rows: List[IngredientRow],
    meal_rows: List[MealRow],
):
    """Extract data from rows and create it.

    If some validation error happens, raise error.
    """
    total = len(ingredient_rows) + len(meal_rows)
    done = 0

    def make_progress():
        nonlocal done, total
        done += 1
        update_task_progress(total, done)

    count_preferences_created = 0
    count_ingredients_created = 0
    count_ingredients_updated = 0
    count_meals_created = 0
    count_meals_updated = 0

    # Create map with all preferences to get preference by name
    all_preferences = Preference.objects.all()
    preferences_ids_map = create_preferences_map(all_preferences)

    # Create preferences which not exists in DB, but exists in ingredients
    created_preferences = get_new_preferences(
        ingredient_rows,
        preferences_ids_map,
    )
    created_preferences_map = create_preferences_map(created_preferences)
    count_preferences_created += len(created_preferences)
    preferences_ids_map.update(created_preferences_map)

    # Create map with all ingredients to get ingredient by name
    all_ingredients = Ingredient.objects.all()
    ingredient_names_map = create_ingredients_map(all_ingredients)

    for row in ingredient_rows:
        validate_ingredient(row)
        ingredient, created = Ingredient.objects.update_or_create(
            name=row.name,
            defaults=dict(
                quantity_type=row.quantity_type,
                is_protein=is_yes(row.is_protein),
                conversion_raw=row.conversion_raw,
                count=is_yes(row.is_count),
            )
        )

        count_ingredients_created += created
        count_ingredients_updated += not created

        preferences = []
        for pref_name in row.preferences:
            if not pref_name:
                continue

            pref_id = generate_preference_id(pref_name)
            preference = preferences_ids_map.get(pref_id)
            if not preference:
                raise exceptions.PreferenceNotFoundExceptions(
                    f'Preference {pref_name} not found'
                )
            preferences.append(preference)

        # Remove old ingredients and add new
        if not created:
            ingredient.preferences.clear()
        ingredient.preferences.add(*preferences)

        # add created ingredient to map
        ingredient_names_map[ingredient.name] = ingredient
        make_progress()

    # Fetch all plans ids, to validate plan ids from file
    all_plan_ids = set(PlanType.objects.all().values_list('id', flat=True))

    for row in meal_rows:
        # Check that plan type exists
        if row.plan_type_id not in all_plan_ids:
            raise exceptions.PlanTypeNotFoundException(
                f'PlanType with id={row.plan_type_id} not found'
            )
        try:
            meal, created = Meal.objects.update_or_create(
                id=row.id or None,
                defaults=dict(
                    name=row.name,
                    breakfast=is_yes(row.breakfast),
                    plan_type_id=row.plan_type_id,
                    prep_instructions='',
                )
            )
        except IntegrityError as e:
            # Try find the meal with same name and plan id, because this pair
            # should be unique.
            existed_meal = Meal.objects.filter(
                name=row.name,
                plan_type_id=row.plan_type_id,
            ).first()
            if existed_meal:
                raise exceptions.DuplicatedMealException(
                    f'Meal "{existed_meal.name}" (id={existed_meal.id}) '
                    f'already exists for "{row.plan_type_id}" plan.'
                )
            raise e

        count_meals_created += created
        count_meals_updated += not created

        if not created:
            meal.ingredients.all().delete()
            meal.mods.all().delete()

        # Create ingredients and modifiers, if exists
        meal_ingredients: List[MealIngredient] = []
        meal_modifiers: List[MealModifier] = []
        used_ingredients: List[Ingredient] = []
        for ingredient_data in row.ingredients:
            if not ingredient_data:
                continue

            ingredient = ingredient_names_map.get(ingredient_data.from_name)

            # ingredient not found
            if not ingredient:
                raise exceptions.IngredientNotFoundException(
                    f'Ingredient {ingredient_data.from_name} not found'
                )

            # duplicated ingredient
            if ingredient in used_ingredients:
                raise exceptions.DuplicatedIngredientException(
                    f'Duplicated ingredient {ingredient.name} '
                    f'in {meal.name} meal'
                )

            if not ingredient_data.quantity:
                raise exceptions.InvalidIngredientQuantityException(
                    f'Quantity for ingredient "{ingredient.name}" in '
                    f'"{meal.name}" meal should be greater then 0'
                )

            try:
                validate_decimal(ingredient_data.quantity)
            except Exception as e:
                raise exceptions.InvalidDataException(
                    f'{meal.name} has ingredient with invalid quantity '
                    f'"{ingredient_data.quantity}"'
                )

            meal_ingredient = MealIngredient(
                meal=meal,
                ingredient=ingredient,
                quantity=ingredient_data.quantity,
            )

            meal_ingredients.append(meal_ingredient)
            used_ingredients.append(ingredient)

            if not ingredient_data.mod_type:
                continue

            # ingredient for modifier
            ingredient_to = None
            if ingredient_data.to_name:
                ingredient_to = ingredient_names_map.get(
                    ingredient_data.to_name
                )
                if not ingredient_to:
                    # ingredient not found
                    raise exceptions.IngredientNotFoundException(
                        f'Ingredient {ingredient_data.to_name} not found'
                    )

            try:
                mod_type = ModTypes.NAME_TO_VALUE_MAP[ingredient_data.mod_type]
            except KeyError:
                raise exceptions.InvalidDataException(
                    f'{meal} modifier for {ingredient.name} has wrong type. '
                    f'Allowed values: {ModTypes.ALLOWED_NAMES_STRING}'
                )

            meal_modifier = MealModifier(
                meal=meal,
                ingredient_from=ingredient,
                ingredient_to=ingredient_to,
                mod_type=mod_type,
                is_soft=is_yes(ingredient_data.mod_type),
            )

            meal_modifiers.append(meal_modifier)

        MealIngredient.objects.bulk_create(meal_ingredients)
        MealModifier.objects.bulk_create(meal_modifiers)
        make_progress()

    return dict(
        total=total,
        done=done,
        count_preferences_created=count_preferences_created,
        count_ingredients_created=count_ingredients_created,
        count_ingredients_updated=count_ingredients_updated,
        count_meals_created=count_meals_created,
        count_meals_updated=count_meals_updated,
    )


@transaction.atomic
def import_all_meals_data(
    ingredients_file: IO,
    meals_file: IO,
):
    """Import preferences, ingredients and meals."""

    # Convert ingredients rows to typed objects
    ingredients_rows: List[IngredientRow] = [
        IngredientRow(
            name=row[0],
            quantity_type=row[1],
            is_protein=row[2],
            is_count=row[3],
            conversion_raw=row[4],
            preferences=list(filter(None, row[5:])),
        ) for row in create_csv_reader(ingredients_file)
    ]

    # Convert meal rows to typed objects
    meal_rows: List[MealRow] = []
    for row in create_csv_reader(meals_file):
        # Generate meal_ingredients rows
        meal_ingredients = [
            MealIngredientRow(
                from_name=data[0],
                quantity=data[1],
                mod_type=data[2],
                to_name=data[3],
                flex=data[4],
            )
            for data in chunks(row[4:], 5)
            if data[0]
        ]

        # Generate meal row
        meal = MealRow(
            id=row[0],
            name=row[1],
            plan_type_id=row[2],
            breakfast=row[3],
            ingredients=meal_ingredients,
        )
        meal_rows.append(meal)

    savepoint = transaction.savepoint()

    try:
        result = _create_all_meals_data(ingredients_rows, meal_rows)
    except Exception as e:
        error_message = str(e)
        transaction.savepoint_rollback(sid=savepoint)
        return dict(
            error=error_message,
        )

    transaction.savepoint_commit(sid=savepoint)
    return result
