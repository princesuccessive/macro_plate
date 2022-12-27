from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..models.customers import Customer, CustomerStatus


class CustomerStatusFilter(admin.SimpleListFilter):
    """Allow filtering Customers by annotated `_status` field."""
    title = 'Status'
    parameter_name = '_status'

    def lookups(self, request, model_admin):
        """Return a list of lookup values."""
        return (
            (CustomerStatus.CURRENT, _(CustomerStatus.CURRENT)),
            (CustomerStatus.WEEK_1, _(CustomerStatus.WEEK_1)),
            (CustomerStatus.WEEK_2, _(CustomerStatus.WEEK_2)),
            (CustomerStatus.INACTIVE, _(CustomerStatus.INACTIVE)),
        )

    def queryset(self, request, queryset):
        """Filter queryset depending on value passed."""
        value = self.value()
        if value:
            filter_value = {self.parameter_name: self.value()}
            queryset = queryset.filter(**filter_value)
        return queryset


@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    """Read-only admin page for Customers.

    This admin page is used for easier debugging: searching outdated Customers,
    checking history, etc.

    """
    list_display = (
        'full_name',
        'email',
        'is_active',
        'status',
        'plan_type',
        'first_delivery_date',
        'last_delivery_date',
        'updated_at',
    )

    list_filter = (
        'meal_assignment_paused',
        CustomerStatusFilter,
        'plan_type',
    )

    search_fields = (
        'first_name',
        'last_name',
        'email',
    )

    def has_add_permission(self, request):
        """Forbid adding new Customers."""
        return False

    def has_change_permission(self, request, obj=None):
        """Forbid edition."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Forbid deletion."""
        return False

    def get_queryset(self, request):
        """Annotate with additional data and apply common ordering."""
        qs = super().get_queryset(request)
        return qs.with_full_name().with_status().order_display()
