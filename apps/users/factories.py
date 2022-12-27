import uuid

import factory

from .models import AppUser


class UserFactory(factory.DjangoModelFactory):
    """Factory for generates test User model.

    There are required fields first_name, last_name, username and email.

    """

    class Meta:
        model = AppUser

    @factory.lazy_attribute
    def username(self):
        """Return formatted username."""
        return "user_{0}".format(uuid.uuid4())

    @factory.lazy_attribute
    def email(self):
        """Return formatted email."""
        return "{0}@example.com".format(self.username)


class AdminUserFactory(UserFactory):
    """Factory for generates test User model with admin's privileges."""

    class Meta:
        model = AppUser

    is_superuser = True
    is_staff = True
