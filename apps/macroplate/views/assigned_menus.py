import datetime

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone

from apps.core import views
from apps.core.utils import date_to_ymd
from apps.macroplate.forms import WorkdaySelectForm
from apps.macroplate.forms.assigned_meals import AssignedMealInlineFormSet
from apps.macroplate.forms.assigned_menus import AssignedMenuForm
from apps.macroplate.forms.customer_select import CustomerForDeliverySelect
from apps.macroplate.models import AssignedMenu, Customer, DailySchedule


class AssignedMenuSelectDayView(views.BaseView):
    """View to render day select page for assigned menus."""
    template = 'assigned_menus/select-day.html'

    form_date_select = WorkdaySelectForm

    def render(self, **context):
        """Render page with come context and default forms."""
        return render(self.request, self.template, context=context)

    def get(self, request, *args, **kwargs):
        """Render the schedule page."""
        return self.render(form_date_select=self.form_date_select(initial={
            'date': timezone.now().date(),
        }))

    def post(self, request, *args, **kwargs):
        """Redirect user to dashboard page."""
        form_select = self.form_date_select(self.request.POST)
        if form_select.is_valid():
            date = form_select.cleaned_data.get('date')
            return redirect('assigned-menus', date=date)

        return self.render(form_date_select=form_select)


class AssignedMenuSelectView(views.BaseListView):
    """View for select Assigned menu and display issues."""
    form = CustomerForDeliverySelect
    template_name = 'assigned_menus/select.html'
    paginate_by = 50
    queryset = AssignedMenu.objects.select_related(
        'customer',
        'customer__plan_type',
        'daily_menu',
    ).prefetch_related(
        'assigned_meals',
    ).order_by(
        '-has_issues',
        'customer__plan_type__name',
        'customer__first_name',
        'customer__last_name',
    )
    context_object_name = 'menus'

    def get_queryset(self):
        """Filter all assigned menus by current date."""
        return super().get_queryset().filter(
            daily_menu__date=self.current_date,
        )

    def get_context_data(self, *, object_list=None, form=None, **kwargs):
        """Add current date and form to context."""
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx.update({
            'current_date': self.current_date_str,
            'form': form or self.form(date=self.current_date)
        })
        return ctx

    @property
    def current_date(self) -> datetime.date:
        """Get date parameter from the URL."""
        return self.kwargs.get('date')

    @property
    def current_date_str(self) -> str:
        """Return date parameter from the URL to as an `Y-m-d` string."""
        return date_to_ymd(self.current_date)

    def post(self, request, *args, **kwargs):
        """Open selected menu."""
        form = self.form(request.POST, date=self.current_date)
        if not form.is_valid():
            return self.get(request, request, *args, form=form, **kwargs)

        customer = form.cleaned_data.get('customer')

        assigned_menu_exists = AssignedMenu.objects.filter(
            customer=customer,
            daily_menu__date=self.current_date,
        ).exists()

        # if menu is exists, redirect user to editing page
        if assigned_menu_exists:
            return redirect(
                to='assigned-menus-edit',
                customer_id=customer.id,
                date=self.current_date,
            )

        # Otherwise, show error
        form.add_error(
            None,
            f'No menu assigned to {customer} on {self.current_date_str}. '
            'Please, check schedules and run "Meal Assignment" on the '
            'Dashboard'
        )
        return self.get(request, request, *args, form=form, **kwargs)


class AssignedMenuEditView(views.BaseUpdateView):
    """View for editing Assigned menu."""
    model = AssignedMenu
    context_object_name = 'menu'
    form_class = AssignedMenuForm
    template_name = 'assigned_menus/edit.html'
    queryset = AssignedMenu.objects

    _customer = None
    _date = None

    def get_success_url(self):
        """When form is saved, keep user on editing form."""
        return reverse_lazy(
            'assigned-menus-edit',
            kwargs=dict(
                customer_id=self._customer.id,
                date=self._date,
            )
        )

    def get_object(self, queryset=None):
        """Get assigned menu by customer_id and date."""
        return self.queryset.get(
            customer_id=self._customer.id,
            daily_menu__date=self._date,
        )

    def dispatch(self, request, *args, **kwargs):
        """Get customer and date from params."""
        customer_id = self.kwargs.get('customer_id')

        self._customer = Customer.objects.get(pk=customer_id)
        self._date = self.kwargs.get('date')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Prepare context for showing form."""
        context = super().get_context_data(**kwargs)

        daily_schedule = DailySchedule.objects.get_custom_or_default(
            schedule_date=self._date,
            customer_id=self._customer.id,
        ).first()

        context['daily_schedule'] = daily_schedule
        context['customer'] = self._customer
        context['current_date'] = self._date
        context['assigned_meals'] = AssignedMealInlineFormSet(
            data=self.request.POST or None,
            instance=self.object,
            form_kwargs={
                'meals_qs': self.object.daily_menu.meals.select_related(
                    'plan_type',
                ),
            },
        )
        max_count = context['daily_schedule'].dishes_count
        context['assigned_meals'].max_num = max_count

        # used for display current count of assigned meals by types
        meals_by_types = self.object.assigned_meals_by_types
        context['assigned_meals_by_types'] = meals_by_types

        return context

    def form_valid(self, form):
        """Validate and save assigned meals."""
        # check unique sub meals.
        context = self.get_context_data()
        assigned_meals = context['assigned_meals']

        super().form_valid(form)

        if assigned_meals.is_valid():
            assigned_meals.instance = self.object
            assigned_meals.save()

        self.object.set_meal_types()
        msg = f'Assigned menu for {self._customer} saved!'
        messages.success(self.request, msg)
        return redirect('assigned-menus', date=self._date)
