import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import \
    UserCreateSerializer as DjoserUserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import (Favorite, Follow, Ingredient, Recipe,
                            RecipeIngredientAmount, RecipeTag, ShoppingCart,
                            Tag)
from users.models import User


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
        if self.context['request'].user.is_authenticated:
            return Follow.objects.filter(follower=self.context['request'].user, following=obj).exists()
        return False


class UserCreateSerializer(DjoserUserCreateSerializer):
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'last_name', 'first_name', 'password')



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
        if self.context['request'].user.is_authenticated:
            return Favorite.objects.filter(user=self.context['request'].user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.context['request'].user.is_authenticated:
            return ShoppingCart.objects.filter(user=self.context['request'].user, recipe=obj).exists()
        return False


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    ingredients = IngredientWriteSerializer(
        many=True,
        source='recipe_to_ingredient')
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text', 'cooking_time')


    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError('Время приготовления не может быть меньше 1 минуты!')
        return value
    
    def validate_tags(self, value):
        if value:
            tag_list = []
            for tag in value:
                if tag in tag_list:
                    raise serializers.ValidationError('Теги рецепта не должны повторяться!')
                tag_list.append(tag)
            return value
        raise serializers.ValidationError('У рецепта должен быть минимум 1 тег!')

    def validate_ingredients(self, value):
        if value:
            ingredient_list = []
            for ingredient in value:
                if ingredient['amount'] < 1:
                    raise serializers.ValidationError('Количество каждого ингредиента должно быть не меньше 1!')
                if ingredient['id'] in ingredient_list:
                    raise serializers.ValidationError('Ингредиенты рецепта не должны повторяться!')
                ingredient_list.append(ingredient['id'])
            return value
        raise serializers.ValidationError('У рецепта должен быть минимум 1 ингредиент!')
        
        
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

    def validate(self, data):
        if Favorite.objects.filter(user=data['user'], recipe=data['recipe']).exists():
            raise serializers.ValidationError('Невозможно добавить рецепт в избранное, так как он уже был добавлен!')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SubscribeFavoriteRecipeSerializer(instance=instance.recipe, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        if ShoppingCart.objects.filter(user=data['user'], recipe=data['recipe']).exists():
            raise serializers.ValidationError('Невозможно добавить рецепт в список покупок, так как он уже был добавлен!')
        return data
    
    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SubscribeFavoriteRecipeSerializer(instance=instance.recipe, context=context).data