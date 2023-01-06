from rest_framework import serializers
from users.models import User
import base64
from django.core.files.base import ContentFile
from recipes.models import Ingredient, Tag, Recipe, RecipeTag, RecipeIngredientAmount, ShoppingCart, Favorite, Follow
from rest_framework.validators import UniqueValidator
from django.shortcuts import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]  
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


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

class RecipeIngredientAmountReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')
        
class IngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredientAmount
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientAmountReadSerializer(
        many=True,
        required=True,
        source='recipe_to_ingredient')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()


    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        return Favorite.objects.filter(user=self.context['request'].user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingCart.objects.filter(user=self.context['request'].user, recipe=obj).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    ingredients = IngredientWriteSerializer(
        many=True,
        source='recipe_to_ingredient')
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients_amounts = validated_data.pop('recipe_to_ingredient')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_amount in ingredients_amounts:
            ingredient_id = ingredient_amount['id']
            ingredient = Ingredient.objects.get(id=ingredient_id)
            RecipeIngredientAmount.objects.create(
            recipe=recipe, 
            ingredient=ingredient,
            amount=ingredient_amount['amount']
        )
        for tag in tags:
            recipe.tags.add(tag)
        return recipe

    def update(self, instance, validated_data):
        RecipeIngredientAmount.objects.filter(recipe=instance).delete()
        instance.tags.clear()
        ingredients_amounts = validated_data.pop('recipe_to_ingredient')
        tags = validated_data.pop('tags')
        for ingredient_amount in ingredients_amounts:
            ingredient_id = ingredient_amount['id']
            ingredient = Ingredient.objects.get(id=ingredient_id)
            RecipeIngredientAmount.objects.create(
            recipe=instance, 
            ingredient=ingredient,
            amount=ingredient_amount['amount']
        )
        for tag in tags:
            instance.tags.add(tag)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance=instance, context=context).data


class SubscribeFavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = SubscribeFavoriteRecipeSerializer(many=True)

    class Meta:
        model = User
        fields = ('email', 'id',  'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(follower=self.context['request'].user, following=obj).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()



class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ()

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SubscribeUserSerializer(instance=instance.following, context=context).data

class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SubscribeFavoriteRecipeSerializer(instance=instance.recipe, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SubscribeFavoriteRecipeSerializer(instance=instance.recipe, context=context).data