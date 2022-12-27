from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class ModTypes:
    """Available types for mods."""
    NO = 0
    SUB = 1
    EXTRA = 2

    CHOICES = (
        (NO, _('NO')),
        (SUB, _('SUB')),
        (EXTRA, _('EXTRA')),
    )

    NAME_TO_VALUE_MAP = {
        choice_name: choice_value
        for choice_value, choice_name in CHOICES
    }

    ALLOWED_NAMES_STRING = ", ".join(
        str(CHOICE[1]) for CHOICE in CHOICES
    )


class MealModifier(models.Model):
    """Model for meal modifiers.

    Meal modifiers are used during meal assignment:
    if a customer has a dislike for a meal ingredient,
    we try to substitute it with a different ingredient, or remove completely.

    For that there are 3 mod types: NO (remove), SUB (substitute)
    and EXTRA (add more).

    TODO: currently meal assignment service just fetches the first modifier,
    regardless of its mod type. Meaning, it might add EXTRA,
    or substitute to an ingredient which the customer dislikes as well.
    """
    meal = models.ForeignKey(
        'Meal',
        related_name='mods',
        on_delete=models.CASCADE,
        verbose_name=_('Meal'),
    )

    ingredient_from = models.ForeignKey(
        'Ingredient',
        related_name='mods_from',
        on_delete=models.CASCADE,
        verbose_name=_('Ingredient from'),
    )

    ingredient_to = models.ForeignKey(
        'Ingredient',
        related_name='mods_to',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_('Ingredient to'),
    )

    mod_type = models.PositiveSmallIntegerField(
        default=ModTypes.NO,
        choices=ModTypes.CHOICES,
        verbose_name=_('Modifier type'),
    )

    is_soft = models.BooleanField(
        default=False,
        verbose_name=_('Flex'),
    )

    class Meta:
        verbose_name = _('Meal Modifier')
        verbose_name_plural = _('Meal Modifiers')

        unique_together = (
            ('meal', 'ingredient_from'),
        )

    def __str__(self):
        """Format string representation based on mod type."""
        if self.mod_type == ModTypes.NO:
            return f'NO {self.ingredient_from.name}'

        if self.mod_type == ModTypes.SUB:
            return (
                f'NO {self.ingredient_from.name} '
                f'SUB {self.ingredient_to.name}'
            )

        result_string = f'{self.ingredient_from.name} EXTRA'
        if self.ingredient_to:
            result_string += f' {self.ingredient_to.name}'
        return result_string

    def clean(self):
        """Ensure `ingredient_to` is present for SUB/EXTRA, and None for NO."""
        if self.mod_type == ModTypes.NO and self.ingredient_to_id is not None:
            msg = 'For NO type the second ingredient must be empty'

        elif self.mod_type != ModTypes.NO and self.ingredient_to_id is None:
            msg = 'For SUB/EXTRA type the second ingredient must be not empty'
        else:
            return super().clean()
        raise ValidationError({'ingredient_to': msg})

    @property
    def is_hard(self):
        """Check that mod is hard."""
        return not self.is_soft
