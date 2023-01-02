from rest_framework import serializers
from users.models import User
from recipes.models import Ingredient, Tag, Recipe, RecipeTag, RecipeIngredientAmount, ShoppingCart, Favorite, Follow
from rest_framework.validators import UniqueValidator

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, validators=(UniqueValidator(queryset=User.objects.all(), message="Данный email уже сущестует"),))
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',  'username', 'first_name', 'last_name', 'is_subscribed')


    def get_is_subscribed(self, obj):
        return Follow.objects.filter(follower=self.context['request'].user, following=obj).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, validators=(UniqueValidator(queryset=User.objects.all(), message="Данный email уже сущестует"),))

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'last_name', 'first_name')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag

class IngredientSerializer(serializers.ModelSerializer):
     
     class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient

class RecipeIngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')
        



class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientAmountSerializer(
        many=True,
        required=True,
        source='recipe')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()


    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        return Favorite.objects.filter(user=self.context['request'].user, recipes=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingCart.objects.filter(user=self.context['request'].user, recipes=obj).exists()