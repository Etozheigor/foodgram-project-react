from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (Favorite, Follow, Ingredient, Recipe, ShoppingCart,
                            Tag)
from users.models import User
from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import AuthorOrAdminOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          ShoppingCartSerializer, SubscribeSerializer,
                          SubscribeUserSerializer, TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = (AuthorOrAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
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
            {'errors': 'Невозможно удалить рецепт из списка'
             f'{model._meta.verbose_name_plural.title()},'
             'так как он еще не был добавлен!'},
            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        return self.post_delete_for_actions(
            model=Favorite, serializer=FavoriteSerializer, pk=pk)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        return self.post_delete_for_actions(
            model=ShoppingCart, serializer=ShoppingCartSerializer, pk=pk)

    @action(methods=['GET'], detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredient_list = request.user.shopping_cart.all().values_list(
            'recipe__recipe_to_ingredient__ingredient',).annotate(
                amount=Sum('recipe__recipe_to_ingredient__amount'))
        shopping_cart = {}
        for ingredient_amount in ingredient_list:
            ingredient = get_object_or_404(Ingredient, id=ingredient_amount[0])
            amount = ingredient_amount[1]
            name_in_shopping_cart = (
                f'{ingredient.name}'
                f'({ingredient.measurement_unit})')
            if shopping_cart.get(name_in_shopping_cart):
                shopping_cart[name_in_shopping_cart] = (
                    shopping_cart[name_in_shopping_cart] + amount)
            else:
                shopping_cart[name_in_shopping_cart] = amount
        if len(shopping_cart.keys()) == 0:
            return Response({'errors': 'Невозможно скачать список покупок'
                             'так как он пуст!'},
                            status=status.HTTP_400_BAD_REQUEST)
        file_name = 'shopping_cart_to_download'
        lines = []
        for ingredient in shopping_cart.keys():
            lines.append(f'- {ingredient} - {shopping_cart[ingredient]}')
        response_content = '\n'.join(lines)
        response = HttpResponse(
            response_content, content_type="text/plain, charset=utf8")
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return response


@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
def subscribe(request, pk):
    """Вью-функция для подписок."""
    follower = request.user
    following = get_object_or_404(User, id=pk)
    context = {'request': request}
    if request.method == 'POST':
        if Follow.objects.filter(follower=follower,
                                 following=following).exists():
            return Response(
                {'errors': 'Невозможно подписаться'
                 'так как вы уже подписаны!'},
                status=status.HTTP_400_BAD_REQUEST)
        elif follower == following:
            return Response(
                {'errors': 'Невозможно подписаться на самого себя!'},
                status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.create(follower=follower, following=following)
        return Response(
            SubscribeUserSerializer(following, context=context).data,
            status=status.HTTP_201_CREATED)
    if Follow.objects.filter(follower=follower, following=following).exists():
        Follow.objects.get(follower=follower, following=following).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(
        {'errors': 'Невозможно отписаться, '
         'так как вы еще не подписаны!'},
        status=status.HTTP_400_BAD_REQUEST)


class SubscribtionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Кастомный Вьюсет для Get-запроса к подпискам."""

    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return user.followings.all()
