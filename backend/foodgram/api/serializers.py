import base64
import logging

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import (
    Ingredient, IngredientAmount, Recipe, RecipeTag, Tag)

User = get_user_model()

logger = logging.getLogger()


class CustomUserSerializer(UserSerializer):
    """Сериализатор модели User."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request_user = self.context.get('request').user.id
        return obj.subscribers.filter(user=request_user).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed', 'recipes_count', 'recipes')

    def get_is_subscribed(self, obj):
        request_user = self.context.get('request').user.id
        return obj.subscribers.filter(user=request_user).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        serializer = RecipeSubscSerializer(
            recipes, many=True, context={'request': request})
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class Base64ImageField(serializers.ImageField):
    """Сериализатор фото."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор Ингредиентов."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientAmountCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания Ингредиент."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
        write_only=True
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True,
        source='ingredientamount',
    )
    image = Base64ImageField()
    author = CustomUserSerializer()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'text', 'cooking_time', 'is_favorited',
            'is_in_shopping_cart', 'image')
        read_only_fields = ('id', 'author')

    def get_is_favorited(self, obj):
        if self.context.get('request').user.is_authenticated:
            return obj.favorites.filter(
                user=self.context['request'].user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.context.get('request').user.is_authenticated:
            return obj.recipe_carts.filter(
                user=self.context['request'].user).exists()
        return False

    def create_ingredients(self, ingredients_data, recipe):
        ingredient_amounts = [
            IngredientAmount(
                recipe=recipe, ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ]
        IngredientAmount.objects.bulk_create(ingredient_amounts)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags_data:
            RecipeTag.objects.create(recipe=recipe, tag=tag)
        self.create_ingredients(
            ingredients_data=ingredients_data, recipe=recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if tags_data is not None:
            instance.tags.set(tags_data)
        if ingredients_data is not None:
            IngredientAmount.objects.filter(recipe=instance).delete()
            self.create_ingredients(
                ingredients_data=ingredients_data, recipe=instance)
        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['ingredients'] = IngredientAmountSerializer(
            instance.ingredientamount.all(), many=True).data
        return ret


class RecipeCreateSerializer(RecipeSerializer):
    ingredients = IngredientAmountCreateSerializer(many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())


class RecipeSubscSerializer(serializers.ModelSerializer):
    """Сокращённый сериализатор для рецептов."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'cooking_time', 'image')
