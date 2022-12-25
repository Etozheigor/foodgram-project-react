from django.contrib import admin

from .models import Ingredient, Tag, Recipe, RecipeIngredientAmount, RecipeTag, ShoppingCart, Favorite, Follow

class RecipeIngredientAmountInLine(admin.TabularInline):
    model = RecipeIngredientAmount

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    search_fields = ('author', 'name', 'tags')
    inlines = (RecipeIngredientAmountInLine,)

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    inlines = (RecipeIngredientAmountInLine,)

admin.site.register(Tag)
admin.site.register(RecipeIngredientAmount)
admin.site.register(RecipeTag)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)
admin.site.register(Follow)