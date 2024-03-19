from django.contrib import admin

from .models import Ingredient, Recipe, Recipebook, RecipeTags, Tag


class RecipeIngredientInLine(admin.TabularInline):
    """Формирование админки ингредиентов для рецептов."""

    model = Recipebook
    extra = 1


class RecipeTagInLine(admin.TabularInline):
    """Формирование админки тегов для рецептов."""

    model = RecipeTags
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Формирование админки для рецептов."""

    list_display = [
        'name',
        'author',
        'get_count_of_favorites',
    ]
    list_filter = [
        'author',
        'name',
        'tags',
    ]

    @admin.display(description='Количество добавлений в избранное')
    def get_count_of_favorites(self, obj):
        return obj.favorites.count()

    inlines = (RecipeIngredientInLine, RecipeTagInLine)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Класс ингредиентов для админки."""

    list_display = [
        'name',
        'measurement_unit',
    ]

    list_filter = [
        'name',
    ]

    search_fields = [
        'name',
    ]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Класс тегов для админки."""

    list_display = [
        'name',
        'color',
        'slug',
    ]

    search_fields = [
        'name',
    ]

    prepopulated_fields = {'slug': ('name',)}
