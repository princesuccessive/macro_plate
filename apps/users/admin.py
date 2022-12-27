from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import AppUser


@admin.register(AppUser)
class AppUserAdmin(UserAdmin):
    """UI for AppUser model."""

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'fields': ('role',),
        }),
    )

    fieldsets = (
        (None, {
            'fields': (
                'username',
                'password'
            )
        }),
        (_('Personal info'), {
            'fields': (
                'first_name',
                'last_name',
                'email',
            )
        }),
        (_('Permissions'), {
            'fields': (
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
        (_('Important dates'), {
            'fields': (
                'last_login',
                'date_joined'
            )
        }),
    )
