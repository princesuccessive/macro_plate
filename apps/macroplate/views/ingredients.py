from django.urls import reverse_lazy

from apps.core import views

from ..forms import IngredientForm
from ..models import Ingredient


class IngredientListView(views.BaseListView):
    """Renders list of Ingredients."""
    context_object_name = 'ingredient_list'
    model = Ingredient
    template_name = 'ingredients/list.html'
    queryset = Ingredient.objects.prefetch_related('preferences')


class IngredientCreateView(views.BaseCreateView):
    """Renders Ingredient creation page.

    Redirects to Ingredient list after creation.

    """
    context_object_name = 'ingredient'
    model = Ingredient
    form_class = IngredientForm
    template_name = 'ingredients/edit.html'
    success_url = reverse_lazy('ingredient-list')
    queryset = Ingredient.objects.prefetch_related('preferences')


class IngredientUpdateView(views.BaseUpdateView):
    """Renders Ingredient details.

    Redirects to Ingredient list after edition.

    """
    context_object_name = 'ingredient'
    model = Ingredient
    form_class = IngredientForm
    template_name = 'ingredients/edit.html'
    success_url = reverse_lazy('ingredient-list')
    queryset = Ingredient.objects.prefetch_related('preferences')


class IngredientDeleteView(views.BaseDeleteView):
    """Renders Ingredient details.

    Redirects to Ingredient list after deletion.

    """
    context_object_name = 'ingredient'
    model = Ingredient
    template_name = 'ingredients/confirm_delete.html'
    success_url = reverse_lazy('ingredient-list')
