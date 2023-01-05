from rest_framework. routers import DefaultRouter
from .views import TagViewSet, IngredientViewSet, RecipeViewSet, subscribe, SubscribtionsViewSet
from django.urls import include, path

app_name = 'api'

v1_router = DefaultRouter()

v1_router.register('tags', TagViewSet, basename='tag')
v1_router.register('ingredients', IngredientViewSet, basename='ingredient')
v1_router.register('recipes', RecipeViewSet, basename='recipe')
v1_router.register('users/subscriptions', SubscribtionsViewSet,  basename='subscribtions')

urlpatterns = [
    path('', include(v1_router.urls)),
    path('users/<int:pk>/subscribe/', subscribe),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]   