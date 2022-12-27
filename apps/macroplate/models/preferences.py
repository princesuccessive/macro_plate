from django.utils.translation import gettext_lazy as _

from apps.core.models import ModelWithStringID, UniqueNameModel
from apps.core.utils import clear_string


def generate_preference_id(name: str) -> str:
    return clear_string(name).replace(' ', '-').lower()


class Preference(ModelWithStringID, UniqueNameModel):
    """Model for ingredients Preference."""

    class Meta:
        verbose_name = _('Preference')
        verbose_name_plural = _('Preferences')

    def __str__(self):
        return f'{self.name} ({self.id})'

    def save(self, *args, **kwargs):
        """Add the ID if it's not specified."""
        if not self.id:
            self.id = generate_preference_id(self.name)
        super().save(*args, **kwargs)
