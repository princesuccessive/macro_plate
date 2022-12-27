from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = (
    'AppUser',
)

# Solution to avoid unique_together for email
AbstractUser._meta.get_field('email')._unique = False


class UserRoles:
    """Available user roles."""
    CUSTOMER_SERVICE = 'customer_service'
    KITCHEN_STAFF = 'kitchen_staff'


class AppUser(AbstractUser):
    """Custom user model.

    Attributes:
        first_name (str): first name
        last_name (str): last name
        username (str): username (not used)
        email (str): email (should be unique), this is our username field
        is_staff (bool): designates whether the user can log into
            this admin site
        is_active (bool): designates whether this user should be
            treated as active
        date_joined (datetime): when user joined
        role (str): role of the user
    """
    ROLE_CHOICES = [
        (UserRoles.CUSTOMER_SERVICE, 'Customer Service'),
        (UserRoles.KITCHEN_STAFF, 'Kitchen Staff'),
    ]

    # TODO (Khaziev): all prod users have the CUSTOMER_SERVICE role;
    # consider deleting
    role = models.CharField(
        _('Role'),
        max_length=20,
        choices=ROLE_CHOICES,
        default=UserRoles.CUSTOMER_SERVICE,
        help_text=_('The user role.'),
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
