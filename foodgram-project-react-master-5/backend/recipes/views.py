from collections import defaultdict

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import RecipesFilterSet
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAuthorOrIsAuthenticatedOrReadOnly
from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag, Recipebook
from .serializers import (IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeReadSerializer, ShortRecipeSerializer,
                          TagSerializer, ShoppingCartSerializer, FavoriteSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    """ Класс представления для работы с рецептами. """
    
    pagination_class = LimitPageNumberPagination
    queryset = Recipe.objects.prefetch_related(
        'ingredients', 'tags'
    ).select_related('author')
    permission_classes = (IsAuthorOrIsAuthenticatedOrReadOnly,)
    filterset_class = RecipesFilterSet
    filter_backends = (filters.DjangoFilterBackend,)
    
    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        if self.action in ('favorite', 'shopping_cart'):
            return ShortRecipeSerializer
        return RecipeCreateUpdateSerializer
    
    def _create_shopping_cart_or_favorite(self, serializer, request, recipe_id):
        serializer = serializer(data={'user': request.user.id, 'recipe': recipe_id})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def _delete_shopping_cart_or_favorite(self, model, request, recipe_id):
        deleted_instances, _ = model.objects.filter(
            user=request.user,
            recipe=get_object_or_404(Recipe, pk=recipe_id)
        ).delete()
        
        if deleted_instances != 0:
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
    def shopping_cart(self, request, pk=None):
        
        if request.method == 'POST':
            response = self._create_shopping_cart_or_favorite(
                ShoppingCartSerializer, request, pk
            )
            return response
        
        if request.method == 'DELETE':
            response = self._delete_shopping_cart_or_favorite(ShoppingCart, request, pk)
            return response
    
    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        user = request.user
        
        if request.method == 'POST':
            response = self._create_shopping_cart_or_favorite(
                FavoriteSerializer, request, pk
            )
            return response
        
        if request.method == 'DELETE':
            response = self._delete_shopping_cart_or_favorite(Favorite, request, pk)
            return response
    
    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = Recipebook.objects.filter(
            recipe__shopping_carts__user=request.user
        ).values_list(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(Sum('amount')).order_by()
        
        file_content = "Список покупок:\n"
        for name, unit, amount in ingredients:
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
