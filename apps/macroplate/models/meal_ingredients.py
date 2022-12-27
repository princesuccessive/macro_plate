from django.db import models
from django.utils.translation import gettext_lazy as _


class MealIngredient(models.Model):
    """Model for  meal ingredients."""

    meal = models.ForeignKey(
        'Meal',
        related_name='ingredients',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        verbose_name=_('Ingredient'),
    )
    quantity = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        max_length=500,
        verbose_name=_('Quantity'),
    )

    class Meta:
        verbose_name = _('Meal Ingredient')
        verbose_name_plural = _('Meal Ingredients')

    def __str__(self):
        return (f'{self.meal}: {self.quantity} {self.quantity_type} '
                f'of {self.ingredient.name}')

    @property
    def quantity_type(self):
        """Returns quantity type of Ingredient."""
        return self.ingredient.quantity_type

    @property
    def is_protein(self):
        """Check that current ingredient is protein."""
        return self.ingredient.is_protein

    @property
    def is_count(self):
        """Check that current ingredient is countable."""
        return self.ingredient.count

    def get_lbs(self, with_raw=False):
        """Get lbs value for current protein, uncountable meal."""
        if not self.is_protein or self.is_count:
            return None

        value = self.quantity
        return value * self.ingredient.conversion_raw if with_raw else value
