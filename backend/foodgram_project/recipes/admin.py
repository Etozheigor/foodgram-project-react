from django.contrib import admin

from .models import (Favorite, Follow, Ingredient, Recipe,
                     RecipeIngredientAmount, RecipeTag, ShoppingCart, Tag)


class RecipeIngredientAmountInLine(admin.TabularInline):
    model = RecipeIngredientAmount

class RecipetagInLine(admin.TabularInline):
    model = RecipeTag

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    search_fields = ('author__username', 'name', 'tags__name')
    inlines = (RecipeIngredientAmountInLine, RecipetagInLine)
    list_display = ('text', 'name', 'cooking_time', 'author', 'image', 'pub_date', 'favorite_count')

    def favorite_count(self, obj):
        return obj.favorite_recipes.count()

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)
    inlines = (RecipeIngredientAmountInLine,)

admin.site.register(Tag)
admin.site.register(RecipeIngredientAmount)
admin.site.register(RecipeTag)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)
admin.site.register(Follow)