from users.models import User
from recipes.models import Ingredient, Tag, Recipe, RecipeTag, RecipeIngredientAmount, ShoppingCart, Favorite, Follow
from .serializers import TagSerializer, IngredientSerializer, RecipeReadSerializer

from rest_framework import viewsets

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
