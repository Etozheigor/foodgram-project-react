from users.models import User
from django.shortcuts import get_object_or_404
from recipes.models import Ingredient, Tag, Recipe, RecipeTag, RecipeIngredientAmount, ShoppingCart, Favorite, Follow
from .serializers import (TagSerializer, IngredientSerializer, ShoppingCartSerializer,
 RecipeReadSerializer, RecipeWriteSerializer, SubscribeSerializer, SubscribeUserSerializer, FavoriteSerializer)

from rest_framework import viewsets, mixins, generics, views, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.http import HttpResponse
from wsgiref.util import FileWrapper


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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def post_delete_for_actions(self, model, serializer, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = self.request.user
        data = {'user': user.id, 'recipe': pk}
        context = {'request': self.request}
        serializer = serializer(data=data, context=context)
        if self.request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if model.objects.filter(user=user, recipe=recipe).exists():
            model.objects.get(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': f'Невозможно удалить рецепт из списка {model._meta.verbose_name_plural.title()}, так как он еще не был добавлен!'}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk):
        return self.post_delete_for_actions(model=Favorite, serializer=FavoriteSerializer, pk=pk)

    @action(methods=['POST', 'DELETE'], detail=True)
    def shopping_cart(self, request, pk):
        return self.post_delete_for_actions(model=ShoppingCart, serializer=ShoppingCartSerializer, pk=pk)

    @action(methods=['GET'], detail=False)
    def download_shopping_cart(self, request):
        shopping_cart_queryset = request.user.shopping_cart.all()
        shopping_cart_dict = {}
        for shopping_cart in shopping_cart_queryset:
            ingredients_queryset = shopping_cart.recipe.recipe_to_ingredient.all()   
            for ingredient_amount in ingredients_queryset:
                ingredient, amount = ingredient_amount.ingredient, ingredient_amount.amount
                name_in_shopping_cart = f'{ingredient.name} ({ingredient.measurement_unit})'
                if shopping_cart_dict.get(name_in_shopping_cart):
                    shopping_cart_dict[name_in_shopping_cart] = shopping_cart_dict[name_in_shopping_cart] + amount
                else:
                    shopping_cart_dict[name_in_shopping_cart] = amount
        if len(shopping_cart_dict.keys()) == 0:
            return Response({'errors': 'Невозможно скачать список покупок так как он пуст!'}, status=status.HTTP_400_BAD_REQUEST)
        with open('api/shopping_cart_to_download/shopping_cart.txt', 'w', encoding='utf-8') as shopping_cart_file:
            for ingredient in shopping_cart_dict.keys():
                shopping_cart_file.write(f'- {ingredient} - {shopping_cart_dict[ingredient]}\n')
        with open('api/shopping_cart_to_download/shopping_cart.txt', 'r', encoding='utf-8') as shopping_cart_file:      
            return HttpResponse(shopping_cart_file, content_type='text/plain')

        



@api_view(['POST', 'DELETE'])
def subscribe(request, pk):
    follower = request.user
    following = get_object_or_404(User, id=pk)
    context = {'request': request}
    if request.method == 'POST':
        if Follow.objects.filter(follower=follower, following=following).exists():
            return Response({'errors':'Невозможно подписаться так как вы уже подписаны!'}, status=status.HTTP_400_BAD_REQUEST)
        elif follower==following:
            return Response({'errors':'Невозможно подписаться на самого себя!'}, status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.create(follower=follower, following=following)
        return Response(SubscribeUserSerializer(following, context=context).data, status=status.HTTP_201_CREATED)
    if Follow.objects.filter(follower=follower, following=following).exists():
        Follow.objects.get(follower=follower, following=following).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response({'errors':'Невозможно отписаться, так как вы еще не подписаны!'}, status=status.HTTP_400_BAD_REQUEST)


class SubscribtionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        user = self.request.user
        return user.followings.all()