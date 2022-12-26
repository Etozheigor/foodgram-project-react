from rest_framework. routers import DefaultRouter
from .views import TagViewSet, IngredientViewSet
from django.urls import include, path

app_name = 'api'

v1_router = DefaultRouter()

v1_router.register('tags', TagViewSet, basename='tag')
v1_router.register('ingredients', IngredientViewSet, basename='ingredient')

urlpatterns = [
    path('', include(v1_router.urls)),
]