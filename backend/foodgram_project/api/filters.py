from django_filters import FilterSet
from django_filters.rest_framework import (AllValuesMultipleFilter,
                                           BooleanFilter, CharFilter)
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class RecipeFilter(FilterSet):
    """Кастомный фильтр для модели рецептов."""

    author = CharFilter(field_name='author__id')
    tags = AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited']

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite_recipes__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(in_shopping_carts__user=self.request.user)
        return queryset


class IngredientSearchFilter(SearchFilter):
    """Кастомный фильтр для поиска по модели ингредиентов."""

    search_param = 'name'
