from django.contrib import admin

from .models import Ingredient, Tag, Recipe, RecipeIngredientAmount, RecipeTag, ShoppingCart, Favorite


class RecipeAdmin(admin.ModelAdmin):
    search_fields = ('author', 'name', 'tags')

class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name',)

admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredientAmount)
admin.site.register(RecipeTag)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)

