from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomerNote(models.Model):
    """CustomerNote model."""

    customer = models.ForeignKey(
        to='Customer',
        on_delete=models.CASCADE,
        verbose_name=_('Customer'),
        related_name='notes'
    )

    title = models.CharField(
        verbose_name=_('Title'),
        max_length=100,
    )

    text = models.TextField(
        verbose_name=_('Text'),
        max_length=500,
    )

    date = models.DateField(
        verbose_name=_('Date'),
        auto_now_add=True,
    )

    def __str__(self):
        return f'{self.customer.full_name} ({self.date}): {self.title}'
