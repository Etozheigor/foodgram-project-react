from django.db import models
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(verbose_name= 'Название', blank=False, max_length=200)
    measurment_unit = models.CharField(verbose_name='Единица измерения', blank=True, max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurment_unit}'

class Tag(models.Model):
    name = models.CharField(verbose_name= 'Название', blank=False, max_length=200)
    color = models.CharField(verbose_name='Цвет в HEX', null=True, max_length=7)
    slug = models.SlugField(verbose_name='Уникальный слаг', null=True, max_length=200)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name

class Recipe(models.Model):
    text = models.TextField(verbose_name='Описание', blank=False)
    name = models.CharField(verbose_name='Название', blank=False, max_length=200)
    cooking_time = models.PositiveSmallIntegerField(verbose_name='Время приготовления в минутах')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='recipes', null=True)
    image = models.ImageField(upload_to='recipes/', null=True, blank=False)
    tags = models.ManyToManyField(Tag, through='RecipeTag', verbose_name='Теги')
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredientAmount', verbose_name='Ингредиенты', blank=False)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
            return f'Рецепт: {self.name}, Автор: {self.author}'

class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'

    def __str__(self):
        return f'Теги рецепта {self.recipe}'

class RecipeIngredientAmount(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return f'Список ингредиентов для рецепта {self.recipe}'

class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='shopping_cart')
    recipes = models.ManyToManyField(Recipe, verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'Список покупок пользователя {self.user}'

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='favorite')
    recipes = models.ManyToManyField(Recipe, verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Избраный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'Избраные рецепты пользователя {self.user}'

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='following')
    following = models.ManyToManyField(User, verbose_name='Подписки')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'Подписки пользоваеля {self.follower}'