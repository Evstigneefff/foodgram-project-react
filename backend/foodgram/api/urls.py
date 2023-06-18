from rest_framework import routers

from .views import IngredientViewSet, RecipeViewSet, TagViewSet


router = routers.DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'', RecipeViewSet, basename='recipes')

urlpatterns = router.urls
