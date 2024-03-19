from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from PIL import Image

from foodgram_backend.enum import (ImageMaxSize, IngredientMaxLength,
                                   RecipeMaxLength, TagMaxLength)

User = get_user_model()


class Tag(models.Model):
    """Модель для тегов."""

    name = models.CharField(
        max_length=TagMaxLength.NAME.value,
        unique=True,
        verbose_name='Название тега',
        help_text='Необходимо указать название тега',
    )
    color = ColorField(
        verbose_name='Цвет',
        help_text='Необходимо указать цвет',
        max_length=TagMaxLength.COLOR.value,
        unique=True,
    )
    slug = models.SlugField(
        max_length=TagMaxLength.SLUG.value,
        unique=True,
        verbose_name='Слаг',
        help_text='Уникальный URL для тега',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Класс ингредиентов."""

    name = models.CharField(
        max_length=IngredientMaxLength.NAME.value,
        verbose_name='Название ингредиента',
        help_text='Необходимо указать название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=IngredientMaxLength.MEASUREMENT_UNIT.value,
        verbose_name='Единица измерения',
        help_text='Необходимо указать единицу измерения',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_for_ingredient',
            ),

        ]

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    """Модель для рецептов."""

    name = models.CharField(
        max_length=RecipeMaxLength.NAME.value,
        verbose_name='Название рецепта',
        help_text='Необходимо указать название рецепта',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        help_text='Автор рецепта',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTags',
        related_name='recipes',
        verbose_name='Тег рецепта',
        help_text='Необходимо указать тег рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='Recipebook',
        related_name='recipes',
        verbose_name='Ингредиенты',
        help_text='Необходимо указать ингредиенты для рецепта',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        help_text='Дата публикации рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Картинка',
        help_text='Необходимо загрузить картинку для рецепта',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Необходимо указать описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(500)],
        verbose_name='Время приготовления в минутах',
        help_text='Необходимо указать время приготовления в минутах',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipe',
            )
        ]

    def __str__(self):
        return (
            f'Блюдо по рецепту {self.name} автора {self.author} '
            f'обычно готовится в течении {self.cooking_time} минут'
        )

    def clean(self):
        self.name = self.name.capitalize()
        return super().clean()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        pic = Image.open(self.image.path)
        pic.thumbnail(ImageMaxSize.IMAGE_SIZE.value)
        pic.save(self.image.path)


class RecipeTags(models.Model):
    """Модель для связи рецептов и тегов."""
    tags = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['tags', 'recipe'],
                name='unique_recipetags'
            )
        ]

    def __str__(self):
        return f'{self.tags} {self.recipe}'


class Recipebook(models.Model):
    """Модель для связи рецептов и ингредиентов."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100)
        ],
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_recipebook'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} в {self.recipe} {self.amount}'


class Favorite(models.Model):
    """Модель для добавления рецептов в избранное."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]


class ShoppingCart(models.Model):
    """Модель для добавления рецептов в корзину."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Выберите пользователя для добавления в корзину'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Выберите рецепт для добавления в корзину'
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return (
            f'Пользователь {self.user} '
            f'добавил рецепт {self.recipe} в корзину'
        )
