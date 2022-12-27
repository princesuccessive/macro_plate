from django.db import models
from django.utils.translation import gettext_lazy as _


class Meal(models.Model):
    """Model for Meals."""
    name = models.CharField(
        max_length=255,
        blank=False,
        verbose_name=_('Meal Name'),
    )
    breakfast = models.BooleanField(
        default=False,
        verbose_name=_('Breakfast?'),
    )
    plan_type = models.ForeignKey(
        'PlanType',
        on_delete=models.CASCADE,
        related_name='meals',
    )
    prep_instructions = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_('Prep Instructions'),
    )

    class Meta:
        verbose_name = _('Meal')
        verbose_name_plural = _('Meals')
        unique_together = (
            ('name', 'plan_type'),
        )

    def __str__(self):
        meal_type = 'breakfast' if self.breakfast else 'regular'

        return f'{self.name} ({self.plan_type}, {meal_type})'

    @property
    def regular(self):
        """Meal is not the breakfast."""
        return not self.breakfast
