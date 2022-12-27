from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.utils import clear_string


class ModelWithStringID(models.Model):
    """Base class for models with string value as Id."""

    id = models.CharField(
        max_length=255,
        unique=True,
        primary_key=True,
        db_index=True,
        validators=[
            RegexValidator(
                regex=r'^[\w-]+$',
                message=_(
                    'Enter a valid value. '
                    'Use the following symbols: a-z, A-Z, 0-9, `-` or `_`'
                ),
            )
        ],
        verbose_name=_('Id'),
    )

    class Meta:
        abstract = True


class UniqueNameModel(models.Model):
    """Base class for models with unique name."""

    name = models.CharField(
        max_length=50,
        verbose_name=_('Name'),
    )
    name_unique = models.CharField(
        max_length=50,
        editable=False,
        unique=True,
    )

    class Meta:
        abstract = True

    def clean(self):
        """Check that name is unique."""
        clear_name = clear_string(self.name)
        same_objects = self.__class__.objects \
            .filter(name_unique=clear_name) \
            .exclude(pk=self.pk)

        if same_objects.exists():
            class_name = self.__class__.__name__
            raise ValidationError(
                f'The database found a {class_name} with a similar name, '
                'please select another name.'
            )
        super().clean()

    def save(self, *args, **kwargs):
        """Add unique name."""
        self.name_unique = clear_string(self.name)
        super().save(*args, **kwargs)
