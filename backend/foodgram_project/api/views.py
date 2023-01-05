from users.models import User
from django.shortcuts import get_object_or_404
from recipes.models import Ingredient, Tag, Recipe, RecipeTag, RecipeIngredientAmount, ShoppingCart, Favorite, Follow
from .serializers import TagSerializer, IngredientSerializer, RecipeReadSerializer, RecipeWriteSerializer, SubscribeSerializer, SubscribeUserSerializer

from rest_framework import viewsets, mixins, generics, views, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response


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
    return Response({'errors':'Невозможно отписаться, так как вы еще не были подписаны!'}, status=status.HTTP_400_BAD_REQUEST)

class SubscribtionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        user = self.request.user
        return user.followings.all()