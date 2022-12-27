from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import ModelWithStringID


class PlanType(ModelWithStringID):
    """Model for Plan types."""

    name = models.CharField(
        max_length=50,
        verbose_name=_('Name'),
    )

    class Meta:
        verbose_name = _('Plan Type')
        verbose_name_plural = _('Plan Types')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.id
        super().save(*args, **kwargs)
