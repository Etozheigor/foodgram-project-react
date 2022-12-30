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
        fields = ('id', 'name', 'measurment_unit')
        model = Ingredient