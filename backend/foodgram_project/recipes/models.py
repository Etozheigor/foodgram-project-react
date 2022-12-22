from django.db import models
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(verbose_name= 'Название', blank=True, max_length=200)
    measurment_unit = models.CharField(verbose_name='Единица измерения', blank=True, max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

class Tag(models.Model):
    name = models.CharField(verbose_name= 'Название', blank=True, max_length=200)
    color = models.CharField(verbose_name='Цвет в HEX', null=True, max_length=7)
    slug = models.SlugField(verbose_name='Уникальный слаг', null=True, max_length=200)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Recipe(models.Model):
    text = models.TextField(verbose_name='Описание', blank=True)
    name = models.CharField(verbose_name='Название', blank=True, max_length=200)
    cooking_time = models.PositiveSmallIntegerField(verbose_name='Время приготовления (в минутах)')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='recipes', null=True)
    image = models.ImageField(upload_to='recipes/', null=True, blank=True)
    tags = models.ManyToManyField(Tag, through='RecipeTag', verbose_name='Теги', blank=False)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'

class RecipeIngredientAmount(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'