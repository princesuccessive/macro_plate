from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe

from apps.core import views
from apps.core.views import BaseView
from apps.macroplate.forms import CsvFileUploadForm, CustomerForm
from apps.macroplate.models import Customer, PlanType
from apps.macroplate.services.import_customers import import_customers


class CustomerListView(views.BaseListView):
    """Renders list of Customers."""
    context_object_name = 'customer_list'
    template_name = 'customers/list.html'
    queryset = Customer.objects.all().select_related(
        'plan_type',
    ).prefetch_related(
        'preferences',
    ).order_display()

    paginate_by = 100

    def get_queryset(self):
        """If search of filter params were passed we filter queryset.

        Implements the search by full name. Full name has `FirstName LastName`
        format.

        """
        qs = super().get_queryset()
        # Call QuerySet methods inside the `get_queryset` to re-evaluate
        # annotated values and filtration depending on `timezone.now()`.
        # Otherwise the `timezone.now()` is evaluated only once on class level
        # and not re-evaluated when `get_queryset` called.
        # This leads to frozen value in filtration and incorrect behavior
        qs = qs.with_full_name().with_status().display_on_list_view()
        search = self.request.GET.get('search', None)

        if search:
            qs = qs.filter(Q(_full_name__icontains=search))

        qs = self._filter_queryset(qs)

        return qs

    def _filter_queryset(self, qs):
        """Filtеr queryset by status, activity, red, plan source and type."""
        customers_filter = {}

        status = self.request.GET.get('status', None)
        is_active = self.request.GET.get('active', None)
        red = self.request.GET.get('red', None)
        plan_source = self.request.GET.get('plan_source', None)
        plan_type = self.request.GET.get('plan_type', None)

        if status == 'Current':
            customers_filter['_status'] = 'C'
        elif status == 'Week 1':
            customers_filter['_status'] = 'W1'
        elif status == 'Week 2':
            customers_filter['_status'] = 'W2'

        if is_active == "Yes":
            customers_filter['meal_assignment_paused'] = False
        elif is_active == "No":
            customers_filter['meal_assignment_paused'] = True

        if red == "Yes":
            customers_filter['red'] = True
        elif red == "No":
            customers_filter['red'] = False

        if plan_source:
            customers_filter['plan_priority__iexact'] = plan_source

        if plan_type:
            customers_filter['plan_type__name'] = plan_type

        qs = qs.filter(**customers_filter)

        return qs

    def get_context_data(self, **kwargs):
        """Update context with all customer plan types."""
        context = super().get_context_data(**kwargs)
        context['plan_types'] = self._get_plan_types()
        return context

    def _get_plan_types(self):
        """Return all plan types."""
        return PlanType.objects.all().distinct('name').values_list(
            'name',
            flat=True
        )


class CustomerDetailView(views.BaseDetailView):
    """Renders Customer details page."""
    context_object_name = 'customer'
    form_class = CustomerForm
    template_name = 'customers/details.html'
    queryset = Customer.objects.all().select_related(
        'plan_type',
    ).prefetch_related(
        'preferences',
        'excluded_meals',
        'preferred_meals',
        'notes',
    )


class CustomerCreateView(views.BaseCreateView):
    """Renders Customer creation page.

    Redirects to Customer list after creation.

    """
    context_object_name = 'customer'
    queryset = Customer.objects.all()
    form_class = CustomerForm
    template_name = 'customers/create.html'
    success_url = reverse_lazy('customer-list')


class CustomerUpdateView(views.BaseUpdateView):
    """Renders Customer details.

    Redirects to Customer list after edition.

    """
    context_object_name = 'customer'
    queryset = Customer.objects.all().select_related(
        'plan_type'
    ).prefetch_related(
        'preferences',
        'excluded_meals',
        'preferred_meals',
    )
    form_class = CustomerForm
    template_name = 'customers/update.html'
    success_url = reverse_lazy('customer-list')

    def form_invalid(self, form):
        """Error message when trying to edit historical copy of Customer."""
        if form.errors.get('__all__'):
            url = reverse('customer-update', kwargs={'pk': form.instance.latest.id})  # noqa
            msg = (
                f'<div>You are not allowed to edit Customer info on this page.'
                f' <a href="{url}">Click here</a> '
                f'to edit <b>actual</b> Customer info.</div>'
            )
            messages.error(self.request, mark_safe(msg))

        return super().form_invalid(form)


class CustomerDeleteView(views.BaseDeleteView):
    """Renders Customer details.

    Redirects to Customer list after deletion.

    """
    context_object_name = 'customer'
    queryset = Customer.objects.all()
    template_name = 'customers/confirm_delete.html'
    success_url = reverse_lazy('customer-list')


class CustomerImportView(UserPassesTestMixin, BaseView):
    """View to render day select page for dashboard."""
    template = 'customers/import.html'
    form = CsvFileUploadForm

    def test_func(self):
        """Check that user is superuser."""
        return self.request.user.is_superuser

    def render(self, **context):
        """Render page with come context and default forms."""
        return render(
            self.request,
            self.template,
            context=context,
        )

    def get(self, request, *args, **kwargs):
        """Render the schedule page."""
        return self.render(form=self.form())

    def post(self, request, *args, **kwargs):
        """Redirect user to dashboard page."""
        form = self.form(request.POST, request.FILES)
        form.full_clean()
        if not form.is_valid():
            return self.render(form=form)

        clear_customers = form.cleaned_data['clear_customers']
        counters = import_customers(request.FILES['file'], clear_customers)

        messages.success(
            request,
            f"Imported {counters['imported']}/{counters['all']}."
        )

        return self.render(
            form=self.form(),
            not_imported_rows=counters['not_imported'].items(),
            warnings=counters['warnings'].items(),
        )
