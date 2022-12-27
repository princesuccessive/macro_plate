from django.db import models
from django.utils.translation import gettext_lazy as _


class AssignedMealType:
    """Types for assigned meals."""
    BREAKFAST = 'breakfast'
    LUNCH = 'lunch'

    CHOICES = (
        (BREAKFAST, _('Breakfast')),
        (LUNCH, _('Lunch')),
    )


class AssignedMeal(models.Model):
    """Model for Assigned Meals."""
    meal = models.ForeignKey(
        to='Meal',
        on_delete=models.CASCADE,
        verbose_name=_('Meal'),
    )
    mods = models.CharField(
        blank=True,
        max_length=255,
        verbose_name=_('Mods'),
    )
    assigned_menu = models.ForeignKey(
        to='AssignedMenu',
        on_delete=models.CASCADE,
        verbose_name=_('Assigned menu'),
        related_name='assigned_meals'
    )
    meal_type = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        choices=AssignedMealType.CHOICES,
    )

    class Meta:
        verbose_name = _('Assigned Meal')
        verbose_name_plural = _('Assigned Meals')

    def __str__(self):
        return f'{self.assigned_menu} - {self.meal}'

    @property
    def mods_as_list(self):
        """Get list of mods."""
        return self.mods.split(",")
