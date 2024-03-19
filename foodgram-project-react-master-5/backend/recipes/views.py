from collections import defaultdict

from django.db.models import Exists, OuterRef
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.pagination import LimitPageNumberPagination
from api.permissions import IsAuthorOrIsAuthenticatedOrReadOnly

from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .serializers import (IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeReadSerializer, ShortRecipeSerializer,
                          TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    """ Класс представления для работы с рецептами. """

    pagination_class = LimitPageNumberPagination
    queryset = Recipe.objects.prefetch_related(
        'ingredients', 'tags'
    ).select_related('author')
    permission_classes = (IsAuthorOrIsAuthenticatedOrReadOnly, )

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        if self.action in ('favorite', 'shopping_cart'):
            return ShortRecipeSerializer
        return RecipeCreateUpdateSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            if request.method == 'POST':
                return Response(
                    {'error': 'Рецепт не найден'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {'error': 'Рецепт не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        user = request.user

        if request.method == 'POST':
            obj, created = ShoppingCart.objects.get_or_create(
                user=user,
                recipe=recipe
            )
            serializer = self.get_serializer(recipe)
            if created:
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

            return Response(
                {'error': 'Рецепт уже в корзине'},
                status=status.HTTP_400_BAD_REQUEST
            )

        elif request.method == 'DELETE':
            shopping_cart_entry_deleted, _ = ShoppingCart.objects.filter(
                user=user,
                recipe=recipe
            ).delete()

            if shopping_cart_entry_deleted != 0:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Рецепт не найден в корзине'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        user = request.user

        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                raise ValidationError('Рецепт не существует')

            serializer = self.get_serializer(recipe)
            _, created = Favorite.objects.get_or_create(
                user=user,
                recipe=recipe
            )

            if created:
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'error': 'Рецепт уже в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )

        elif request.method == 'DELETE':
            try:
                recipe = Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {'error': 'Рецепт не найден'},
                    status=status.HTTP_404_NOT_FOUND
                )

            deleted_favorite, _ = Favorite.objects.filter(
                user=user,
                recipe=recipe
            ).delete()
            if deleted_favorite:
                return Response(status=status.HTTP_204_NO_CONTENT)
                # Измените код статуса на 400
            return Response(
                {'error': 'Рецепт не в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _handle_action(self, model, request, pk):
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            return Response(
                {'error': 'Несуществующий рецепт'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user

        if request.method == 'POST':
            obj, created = model.objects.get_or_create(
                user=user,
                recipe=recipe
            )
            if not created:
                return Response(
                    {"error": "Уже в списке"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            affected_rows, _ = model.objects.filter(
                user=user,
                recipe=recipe
            ).delete()
            if affected_rows == 0:
                return Response(
                    {"error": "Не найдено в списке"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        tags = self.request.query_params.getlist('tags')
        in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        is_favorited = self.request.query_params.get('is_favorited')
        author_id = self.request.query_params.get('author')
        print("Requested tags:", tags)
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        if in_shopping_cart is not None and user.is_authenticated:
            if in_shopping_cart == '1':
                queryset = queryset.filter(shopping_carts__user=user)
            elif in_shopping_cart == '0':
                queryset = queryset.exclude(shopping_carts__user=user)

        if is_favorited is not None and user.is_authenticated:
            if is_favorited == '1':
                favorites = Favorite.objects.filter(
                    user=user,
                    recipe=OuterRef('pk')
                )
                queryset = queryset.annotate(
                    is_favorited=Exists(favorites)
                ).filter(is_favorited=True)
            elif is_favorited == '0':
                queryset = queryset.annotate(
                    is_favorited=Exists(Favorite.objects.filter(
                        user=user,
                        recipe=OuterRef('pk')
                    ))
                ).filter(is_favorited=False)

        if author_id is not None:
            queryset = queryset.filter(author__id=author_id)

        print("Filtered queryset:", queryset)
        return queryset

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart_recipes = ShoppingCart.objects.filter(
            user=user
        ).select_related('recipe')

        if not shopping_cart_recipes.exists():
            return Response(
                {'detail': 'Список покупок пуст.'},
                status=status.HTTP_204_NO_CONTENT
            )

        ingredients_list = defaultdict(int)
        for cart_item in shopping_cart_recipes:
            for ingredient in cart_item.recipe.recipebook_set.all():
                name = ingredient.ingredient.name
                amount = ingredient.amount
                unit = ingredient.ingredient.measurement_unit
                ingredients_list[(name, unit)] += amount

        file_content = "Список покупок:\n"
        for (name, unit), amount in ingredients_list.items():
            file_content += f"{name} - {amount} {unit}\n"

        response = HttpResponse(file_content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Предоставляет доступ только для чтения к тегам.
    Доступен всем пользователям, без ограничений по авторизации.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
