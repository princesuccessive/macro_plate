from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.macroplate.models.assigned_meals import AssignedMealType


class AssignedMenu(models.Model):
    """Model for Assigned Menu."""
    customer = models.ForeignKey(
        to='Customer',
        on_delete=models.CASCADE,
        verbose_name=_('Customer'),
    )
    daily_menu = models.ForeignKey(
        to='DailyMenu',
        on_delete=models.CASCADE,
        verbose_name=_('Daily Menu'),
    )
    has_issues = models.BooleanField(
        default=False,
        verbose_name=_('Has issues'),
    )

    class Meta:
        verbose_name = _('Assigned Menu')
        verbose_name_plural = _('Assigned Menus')
        unique_together = (
            ('customer', 'daily_menu'),
        )

    def __str__(self):
        return f'{self.daily_menu} - {self.customer}'

    @property
    def daily_schedule(self):
        """Get daily schedule for this assigned menu."""
        return self.customer.daily_schedules.get(date=self.daily_menu.date)

    @property
    def valid_meals_count(self):
        """Get right count of all dishes for this assigned menu."""
        return self.daily_schedule.dishes_count

    @property
    def assigned_meals_by_types(self):
        """Return all assigned meals separated by type."""
        meals_by_type = {
            AssignedMealType.BREAKFAST: [],
            AssignedMealType.LUNCH: [],
        }

        for assigned_meal in self.assigned_meals.all():
            if assigned_meal.meal_type:
                meals_by_type[assigned_meal.meal_type].append(assigned_meal)

        return meals_by_type

    @classmethod
    def get_reset_or_create(cls, **kwargs) -> 'AssignedMenu':
        """Run `get_or_create`, but reset some data if exists.

        Delete previously assigned meals,
        reset `has_issues` to False without saving.
        """
        assigned_menu: AssignedMenu
        assigned_menu, created = cls.objects.get_or_create(**kwargs)

        if not created:
            assigned_menu.assigned_meals.all().delete()
            assigned_menu.has_issues = False

        return assigned_menu

    def set_meal_types(self):
        """When assigned menu has changed (or meals), update types of meals.

        This function return boolean value, which indicates that all meals
        filled or not.
        """
        meals = self.assigned_meals.all()
        schedule = self.customer.daily_schedules.get(date=self.daily_menu.date)
        breakfasts_count = schedule.breakfasts
        lunches_count = schedule.lunches

        # breakfasts
        breakfasts = meals.filter(meal__breakfast=True)
        for assigned_meal in breakfasts:
            breakfasts_count -= 1
            assigned_meal.meal_type = AssignedMealType.BREAKFAST
            assigned_meal.save()

        regulars = meals.filter(meal__breakfast=False)
        for assigned_meal in regulars:
            if lunches_count > 0:
                assigned_meal.meal_type = AssignedMealType.LUNCH
                lunches_count -= 1
            else:
                break
            assigned_meal.save()
