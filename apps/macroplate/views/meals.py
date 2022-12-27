from functools import partial
from typing import Union

from django.forms import model_to_dict
from django.urls import reverse_lazy

from apps.core import views
from apps.macroplate import forms

from ..models import Meal


class MealListView(views.BaseListView):
    """Renders list of Meal."""
    model = Meal
    context_object_name = 'meal_list'
    queryset = Meal.objects \
        .select_related('plan_type') \
        .prefetch_related('ingredients') \
        .order_by('name', 'plan_type__name')
    template_name = 'meals/list.html'


class MealDetailView(views.BaseDetailView):
    """Renders Meal details page."""
    model = Meal
    context_object_name = 'meal'
    form_class = forms.MealForm
    queryset = Meal.objects \
        .select_related('plan_type') \
        .prefetch_related('ingredients')
    template_name = 'meals/details.html'


class MealValidationMixinView:
    def form_invalid(self, form, form_ingredients=None, form_mods=None):
        """Pass additional sub forms to get_context_data function."""
        return self.render_to_response(self.get_context_data(
            form=form,
            form_ingredients=form_ingredients,
            form_mods=form_mods,
        ))

    def get_context_data(
        self,
        form_ingredients=None,
        form_mods=None,
        **kwargs,
    ):
        """Add sub forms to context."""
        context = super().get_context_data(**kwargs)

        if form_ingredients:
            context['ingredients'] = form_ingredients

        if form_mods:
            context['mods'] = form_mods

        return context

    def form_valid(self, form):
        """Save ingredients & mods if form valid."""
        context = self.get_context_data()
        ingredients = context['ingredients']
        mods = context['mods']

        if ingredients.is_valid() and mods.is_valid():
            # check that all ingredients_to in mods exists in meal
            ingredients, mods, error = self._check_mods(
                form_ingredients=ingredients,
                form_mods=mods,
            )

            if error:
                return self.form_invalid(form, ingredients, mods)

            instance = form.save()
            ingredients.instance = instance
            mods.instance = instance
            ingredients.save()
            mods.save()
            return super().form_valid(form)
        return self.form_invalid(form, ingredients, mods)

    def _check_mods(self, form_ingredients, form_mods):
        """Check that all ingredients_from in mods exits in meal.

        Return updated forms, and boolean flag, that indicates an error:
        >>> ingredients, mods, error = self._check_mods(...)
        """
        ingredient_set = set()
        for sub_form in form_ingredients.forms:
            if not sub_form.is_valid():
                continue

            if sub_form.cleaned_data.get('DELETE'):
                continue

            ingredient_set.add(sub_form.cleaned_data.get('ingredient'))

        error = False
        for sub_form in form_mods.forms:
            if not sub_form.is_valid():
                continue

            if sub_form.cleaned_data.get('DELETE'):
                continue

            ingredient_from = sub_form.cleaned_data.get('ingredient_from')
            ingredient_to = sub_form.cleaned_data.get('ingredient_to')

            if not ingredient_from and not ingredient_to:
                continue

            if ingredient_from not in ingredient_set:
                error = True
                sub_form.add_error(
                    'ingredient_from',
                    'This ingredient not found in this meal',
                )

        return form_ingredients, form_mods, error


class MealCreateView(MealValidationMixinView, views.BaseCreateView):
    """Renders Meal creation page.

    Redirects to Meal list after creation.
    """
    model = Meal
    template_name = 'meals/edit.html'
    form_class = forms.MealForm
    context_object_name = 'meal'
    success_url = reverse_lazy('meal-list')
    queryset = Meal.objects \
        .select_related('plan_type') \
        .prefetch_related('ingredients')

    def get_context_data(self, **kwargs):
        """Get context data for template."""
        data = super().get_context_data(**kwargs)

        # get initial data for ingredients
        initial = self._get_initial_related_data()

        if 'ingredients' not in data:
            # create formset for ingredients and add this to context
            formset_ingredients = forms.create_meal_ingredient_formset(
                extra=len(initial['ingredients']) or 1,
            )
            data['ingredients'] = formset_ingredients(
                data=self.request.POST or None,
                initial=initial['ingredients'],
            )

        if 'mods' not in data:
            # create formset for modifiers and add this to context
            formset_modifiers = forms.create_meal_modifier_formset(
                extra=len(initial['mods']) or 1,
            )
            data['mods'] = formset_modifiers(
                data=self.request.POST or None,
                initial=initial['mods'],
            )

        # validate form, for showing errors
        if self.request.POST:
            data['mods'].is_valid()
            data['ingredients'].is_valid()

        return data

    def get_initial(self):
        """Get initial data for MealForm.

        Copy all fields (exists in MealForm to new form) (without
        ingredients and mods). Ingredients will be copied in get_context_data()
        method
        """
        initial = super().get_initial()
        initial_object = self._get_copy_object()

        if initial_object:
            form = forms.MealForm(instance=initial_object)
            initial.update(form.initial)

        return initial

    def _get_initial_related_data(self):
        """Get initial data for ingredients and mods."""
        obj = self._get_copy_object()
        ingredients = []
        mods = []

        serializer = partial(model_to_dict, exclude=['id', 'meal'])
        if obj and not self.request.POST:
            ingredients = map(serializer, obj.ingredients.all())
            mods = map(serializer, obj.mods.all())

        return {"ingredients": list(ingredients), "mods": list(mods)}

    def _get_copy_object(self) -> Union[Meal, None]:
        """Get the instance that we need to copy."""
        copy_id = self.request.GET.get('copy_id')

        if not copy_id:
            return None

        return Meal.objects.filter(pk=copy_id).first()


class MealUpdateView(MealValidationMixinView, views.BaseUpdateView):
    """View for update Meal.

    Redirects to Meal list after saving.

    """
    model = Meal
    context_object_name = 'meal'
    form_class = forms.MealForm
    template_name = 'meals/edit.html'
    success_url = reverse_lazy('meal-list')
    queryset = Meal.objects \
        .select_related('plan_type') \
        .prefetch_related('ingredients')

    def get_context_data(self, **kwargs):
        """Add information about ingredients to context."""
        data = super().get_context_data(**kwargs)

        if 'ingredients' not in data:
            # create formset for ingredients and add this to context
            formset_ingredients = forms.create_meal_ingredient_formset()
            data['ingredients'] = formset_ingredients(
                data=self.request.POST or None,
                instance=self.object,
            )

        if 'mods' not in data:
            # create formset for mods and add this to context
            formset_modifiers = forms.create_meal_modifier_formset()
            data['mods'] = formset_modifiers(
                data=self.request.POST or None,
                instance=self.object,
            )

        # validate form, for showing errors
        if self.request.POST:
            data['mods'].is_valid()
            data['ingredients'].is_valid()

        return data


class MealDeleteView(views.BaseDeleteView):
    """Renders  Meal details.

    Redirects to  Meal list after deletion.

    """
    model = Meal
    context_object_name = 'meal'
    template_name = 'meals/confirm_delete.html'
    success_url = reverse_lazy('meal-list')
