from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.constants import QuantityType
from apps.core.models import UniqueNameModel


class Ingredient(UniqueNameModel):
    """Ingredient model."""

    quantity_type = models.CharField(
        choices=QuantityType.CHOICES,
        default=QuantityType.OUNCE,
        max_length=25,
        verbose_name=_('Quantity Type'),
    )
    is_protein = models.BooleanField(
        default=False,
        verbose_name=_('Is Protein?'),
    )
    conversion_raw = models.DecimalField(
        default=1,
        max_digits=19,
        decimal_places=4,
        max_length=500,
        verbose_name=_('Conversion Raw'),
        help_text=_('Used only for protein'),
    )
    count = models.BooleanField(
        default=False,
        verbose_name=_('Count?'),
        help_text=_('Used only for protein'),
    )
    preferences = models.ManyToManyField(
        'Preference',
        blank=True,
        related_name='ingredients',
    )

    class Meta:
        verbose_name = _('Ingredient')
        verbose_name_plural = _('Ingredients')

    def __str__(self):
        return f'{self.name} ({str(self.quantity_type)})'

    def clean(self):
        """Additional validation for Quantity Type logic."""
        super().clean()
        self.clean_quantity_type()

    def clean_quantity_type(self):
        """Validation of Quantity type logic.

        There are strict limitations for Quantity types in case when
        `is_protein` == True:
        * if `count` == True - quantity type must be `Count (ct)`;
        * if `count` == False - quantity type must be `Ounces (oz)`.

        In addition, `is_protein` == False && `count` == True forbidden.

        """
        if not self.is_protein and self.count:
            raise ValidationError(
                '"Count" cannot be selected for not Protein Ingredient'
            )

        # Do not check quantity type for not protein Ingredient
        if not self.is_protein:
            return

        if self.count and self.quantity_type != QuantityType.COUNT:
            raise ValidationError(
                {'quantity_type':
                     'Quantity type of countable Ingredient must be "Count"'}
            )

        if not self.count and self.quantity_type != QuantityType.OUNCE:
            raise ValidationError(
                {'quantity_type': 'Quantity type must be "Ounces"'}
            )
