from django.db import models
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(verbose_name= 'Название', max_length=200)
    measurement_unit = models.CharField(verbose_name='Единица измерения', max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'

class Tag(models.Model):
    name = models.CharField(verbose_name= 'Название', unique=True, max_length=200)
    color = models.CharField(verbose_name='Цвет в HEX', null=True, max_length=7)
    slug = models.SlugField(verbose_name='Уникальный слаг', unique=True, max_length=200)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name

class Recipe(models.Model):
    text = models.TextField(verbose_name='Описание')
    name = models.CharField(verbose_name='Название', max_length=200)
    cooking_time = models.PositiveSmallIntegerField(verbose_name='Время приготовления в минутах')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    image = models.ImageField(upload_to='recipes/')
    tags = models.ManyToManyField(Tag, through='RecipeTag', verbose_name='Теги', related_name='tags')
    ingredients = models.ManyToManyField(
        Ingredient, 
        through='RecipeIngredientAmount', 
        verbose_name='Ингредиенты',
        related_name='ingredients'
    )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации',)

    class Meta:
        ordering = ('-pub_date',)
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
        constraints = (models.UniqueConstraint(fields=('recipe', 'tag'), name='unique_recipe_tag'),)

    def __str__(self):
        return f'Теги рецепта {self.recipe}'

class RecipeIngredientAmount(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_to_ingredient')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredient_to_recipe')
    amount = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = (models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_recipe_ingredient'),)

    def __str__(self):
        return f'Список ингредиентов для рецепта {self.recipe}'

class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='shopping_cart')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт', related_name='in_shopping_carts')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = (models.UniqueConstraint(fields=('user', 'recipe'), name='unique_shopping_cart_recipe'),)

    def __str__(self):
        return f'Список покупок пользователя {self.user}'

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='favorite_recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт', related_name='users')
    

    class Meta:
        verbose_name = 'Избраный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (models.UniqueConstraint(fields=('user', 'recipe'), name='unique_favorite_recipe'),)

    def __str__(self):
        return f'Избраные рецепты пользователя {self.user}'

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='followings')
    following = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Подписки', related_name='followers')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (models.UniqueConstraint(fields=('follower', 'following'), name='unique_follow'),)

    def __str__(self):
        return f'Подписки пользоваеля {self.follower}'