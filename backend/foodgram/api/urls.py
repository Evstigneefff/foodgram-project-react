from rest_framework import routers

from .views import IngredientViewSet, RecipeViewSet, TagViewSet


router = routers.DefaultRouter()
router.register(r'api/tags', TagViewSet, basename='tags')
router.register(r'api/ingredients', IngredientViewSet, basename='ingredients')
router.register(r'', RecipeViewSet, basename='recipes')

urlpatterns = router.urls
