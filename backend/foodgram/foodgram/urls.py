from django.contrib import admin
from django.urls import include, path

from rest_framework import routers

from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet


router = routers.DefaultRouter()
router.register(r'api/tags', TagViewSet, basename='tags')
router.register(r'api/ingredients', IngredientViewSet, basename='ingredients')
router.register(r'api/recipes/', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('api/', include('rest_framework.urls', namespace='rest_framework')),
]

urlpatterns += router.urls
