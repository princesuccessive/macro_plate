from django.db import models
from django.utils.translation import gettext_lazy as _


class DailyMenu(models.Model):
    """Model to describe all the Meals prepared for the day."""
    date = models.DateField(
        blank=False,
        db_index=True,
        verbose_name=_('Date'),
        unique=True,
    )
    meals = models.ManyToManyField(
        to='Meal',
        through='DailyMenuItem',
        verbose_name=_('Meals'),
        related_name='daily_menus',
    )

    class Meta:
        verbose_name = _('Daily Menu')
        verbose_name_plural = _('Daily Menus')

    def __str__(self):
        return f'Daily Menu for {self.date}'


class DailyMenuItem(models.Model):
    """A custom `through` model for Meals of Daily Menus to store order."""
    daily_menu = models.ForeignKey('DailyMenu', on_delete=models.CASCADE)
    meal = models.ForeignKey('Meal', on_delete=models.CASCADE)
    order = models.IntegerField()
