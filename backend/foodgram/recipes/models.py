from django.contrib.auth import get_user_model

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from rest_framework.exceptions import ValidationError

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиенты."""

    name = models.CharField(max_length=64, verbose_name="Название")
    measurement_unit = models.CharField(max_length=16, verbose_name="Единица измерения")

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(unique=True, max_length=64, verbose_name="Название")
    color = models.CharField(unique=True, max_length=16, verbose_name="Цвет")
    slug = models.SlugField(unique=True, verbose_name="Адрес")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    MIN_VALUE = 1
    MAX_VALUE = 4320
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта",
    )
    name = models.CharField(max_length=64, verbose_name="Название")
    text = models.TextField(verbose_name="Описание")
    tags = models.ManyToManyField(
        Tag,
        through="RecipeTag",
        through_fields=("recipe", "tag"),
        verbose_name="Список id тегов",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientAmount",
        through_fields=("recipe", "ingredient"),
        verbose_name="Список ингредиентов",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления (в минутах)",
        validators=[MinValueValidator(MIN_VALUE), MaxValueValidator(MAX_VALUE)],
    )
    pub_date = models.DateTimeField("Дата добавления", auto_now_add=True, db_index=True)
    image = models.ImageField(upload_to="recipes/", verbose_name="Картинка")

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-pub_date"]

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    """Вспомогательная модель ГецептТег."""

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="tagrecipes",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="tagrecipes",
    )

    class Meta:
        verbose_name = "РецептТег"
        verbose_name_plural = "РецептТег"
        ordering = ["-recipe"]

    def __str__(self):
        return f"Рецепт {self.recipe}, тег {self.tag}"


class IngredientAmount(models.Model):
    """Вспомогательная модель ИнгредиентКоличество."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredientamount",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredientamount",
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество в рецепте",
    )

    class Meta:
        verbose_name = "ИнгредиентКоличество"
        verbose_name_plural = "ИнгредиентКоличество"
        ordering = ["-recipe"]

    def __str__(self):
        return f"Рецепт {self.recipe}, ингредиент {self.ingredient}"


class Favorite(models.Model):
    """Модель избранное."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Рецепт",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="В избранном у",
    )

    def clean(self):
        if Favorite.objects.filter(user=self.user, recipe=self.recipe).exists():
            raise ValidationError('Рецепт уже есть в избранном')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        ordering = ["-recipe"]

    def __str__(self):
        return f"Рецепт {self.recipe}, в избранном у {self.user}"


class Cart(models.Model):
    """Модель корзины покупок."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_carts",
        verbose_name="Рецепт списке покупок",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_carts",
        verbose_name="Владелец списка покупок",
    )

    def clean(self):
        if Cart.objects.filter(user=self.user, recipe=self.recipe).exists():
            raise ValidationError('Рецепт уже есть в корзине')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        ordering = ["-recipe"]

    def __str__(self):
        return f"Рецепт {self.recipe}, в списке покупок у {self.user}"
