from api.mixins import GetSerializerClassMixin
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Cart, Favorite, Ingredient, IngredientAmount,
                            Recipe, Tag)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import RecipeFilter
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, RecipeSubscSerializer,
                          TagSerializer)

User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet для модели тегов."""
    permission_classes = (AllowAny,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """ViewSet для модели ингредиентов."""
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    queryset = Ingredient.objects.all()

    def get_queryset(self):
        name = self.request.GET.get('name')
        if name:
            return self.queryset.filter(
                name__icontains=name)
        return super().queryset


class RecipeViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    """ViewSet для модели рецептов."""
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    serializer_class_by_action = {
        'create': RecipeCreateSerializer,
        'partial': RecipeCreateSerializer,
    }

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, context={}, *args, **kwargs):
        context['request'] = request
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = request.user

        if request.method == 'POST':
            Favorite.objects.create(recipe=recipe, user=user)
            serializer = RecipeSubscSerializer(recipe, context=context)
            return Response(serializer.data, status.HTTP_201_CREATED)

        get_object_or_404(Favorite, recipe=recipe, user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, context={}, *args, **kwargs):
        context['request'] = request
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = request.user

        if request.method == 'POST':
            Cart.objects.create(recipe=recipe, user=user)
            serializer = RecipeSubscSerializer(recipe, context=context)
            return Response(serializer.data, status.HTTP_201_CREATED)

        get_object_or_404(Cart, recipe=recipe, user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request, context={}, *args, **kwargs):
        context['request'] = self.request
        user = request.user
        queryset = IngredientAmount.objects.filter(
            recipe__recipe_carts__user=user).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
            total_amount=Sum('amount')
        ).order_by()

        shopping_list = render_to_string(
            'shopping_list.txt', {'shopping_list': queryset}
        )
        shopping_list = shopping_list.strip().replace('\n\n', '\n')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)
