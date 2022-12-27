import json

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.core.views import BaseView
from apps.macroplate import forms
from apps.macroplate.api.serializers import (
    DailyMenuItemSerializer,
    MealSerializer,
)
from apps.macroplate.models import DailyMenu, Meal
from apps.macroplate.models.daily_menu import DailyMenuItem
from apps.macroplate.services import DailyMenuService


class DailyMenuSelectView(BaseView):
    """View to render daily menu select page."""
    template = 'daily_menu/select.html'

    form_date_select = forms.WorkdaySelectForm

    def render(self, **context):
        """Render page with come context and default forms."""
        return render(self.request, self.template, context=context)

    def get(self, request, *args, **kwargs):
        """Render the schedule page."""
        return self.render(form_date_select=self.form_date_select(initial={
            'date': timezone.now().date(),
        }))

    def post(self, request, *args, **kwargs):
        """Redirect user to page with menu."""
        form_select = self.form_date_select(self.request.POST)
        if form_select.is_valid():
            date = form_select.cleaned_data.get('date')
            return redirect('daily-menu-edit', date=date)

        return self.render(form_date_select=form_select)


class DailyMenuEditView(BaseView):
    """View to render daily menu page."""
    template = 'daily_menu/index.html'

    form_date_select = forms.WorkdaySelectForm

    def dispatch(self, request, *args, **kwargs):
        """Validate the date, and if it;s invalid - redirect user."""
        if not kwargs.get('date'):
            return redirect('daily-menu')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Render the schedule page."""
        return self._render()

    def post(self, request, *args, **kwargs):
        """Perform some actions by POST request"""
        return self._copy(request, *args, **kwargs)

    def _render(self, **context):
        """Render page with come context and data for js."""
        form_date = context.get(
            'form_date',
            self.form_date_select(initial={'date': self._get_date()})
        )

        form_date_copy = context.get('form_date_copy', self.form_date_select())
        form_date_copy.fields['date'].label = "Copy this menu to"

        # get list of all meals
        meals = Meal.objects.prefetch_related('plan_type').all()
        serializer = MealSerializer(instance=meals, many=True)
        serialized_meals = json.dumps(serializer.data)

        menu, _ = DailyMenu.objects.get_or_create(date=self._get_date())

        menu_items = DailyMenuItem.objects.filter(
            daily_menu=menu
        ).order_by('order')
        serializer = DailyMenuItemSerializer(instance=menu_items, many=True)
        serialized_menu_items = json.dumps(serializer.data)

        default_context = dict(
            form_date=form_date,
            form_date_copy=form_date_copy,
            date=self._get_date(),
            meals=serialized_meals,
            menu_items=serialized_menu_items,
        )
        return render(self.request, self.template, context={
            **default_context,
            **context,
            'allowOrder': True,
        })

    def _copy(self, request, *args, **kwargs):
        """Copy current menu to another date."""
        form_date_copy = self.form_date_select(request.POST)
        if not form_date_copy.is_valid():
            return self._render(form_date_copy=form_date_copy)

        copy_to_date = form_date_copy.cleaned_data.get('date')
        DailyMenuService.copy_from_date_to_date(
            from_date=self._get_date(),
            to_date=copy_to_date,
        )

        messages.success(request, 'Menu copied successfully!')

        return self._render()

    def _get_date(self):
        return self.kwargs.get('date')


class DailyMenuSaveView(BaseView):
    """View to save daily menu via Ajax request."""

    form_date_select = forms.WorkdaySelectForm

    def post(self, request, *args, **kwargs):
        """Perform daily menu saving."""
        data = json.loads(request.body)
        new_items = data.get('items')

        menu, _ = DailyMenu.objects.get_or_create(date=self._get_date())
        old_items = list(DailyMenuItem.objects.filter(daily_menu_id=menu.id))

        items_to_create = []
        items_to_update = []
        items_to_delete_ids = []

        # Compute items to update and items to delete
        for old_item in old_items:
            for new_item in new_items:
                if new_item['id'] == old_item.id:
                    old_item.order = new_item['order']
                    old_item.meal_id = new_item['meal_id']
                    items_to_update.append(old_item)
                    break
            else:
                items_to_delete_ids.append(old_item.id)

        # Compute items to create
        for new_item in new_items:
            if not new_item['id']:
                items_to_create.append(DailyMenuItem(
                    meal_id=new_item['meal_id'],
                    order=new_item['order'],
                    daily_menu=menu
                ))

        DailyMenuItem.objects.bulk_create(items_to_create)
        DailyMenuItem.objects.bulk_update(
            items_to_update,
            fields=['order', 'meal_id'],
        )
        DailyMenuItem.objects.filter(id__in=items_to_delete_ids).delete()

        messages.success(request, "Daily menu successfully saved")
        return JsonResponse({"message": 'ok'})

    def _get_date(self):
        return self.kwargs.get('date')
