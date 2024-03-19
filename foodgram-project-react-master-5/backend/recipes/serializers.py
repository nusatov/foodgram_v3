from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

import users.serializers
from foodgram_backend.enum import RecipeMaxLength
from .fields import Base64ImageField
from .models import Favorite, Ingredient, Recipe, Recipebook, ShoppingCart, Tag


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели тегов.
    Преобразует данные тегов для передачи через API.
    """
    
    name = serializers.CharField()
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""
    
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipebookSerializer(serializers.ModelSerializer):
    """ Сериализатор для книги рецептов. """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name', required=False)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
        required=False
    )
    
    class Meta:
        model = Recipebook
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    author = users.serializers.UserReadSerializer()
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    ingredients = RecipebookSerializer(
        source='recipebook_set',
        many=True,
    )
    image = Base64ImageField()
    
    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = fields
    
    def get_is_favorited(self, recipe) -> bool:
        request = self.context.get('request')
        return (
                request is not None
                and request.user.is_authenticated
                and Favorite.objects.filter(
            user=request.user.id, recipe=recipe
        ).exists()
        )
    
    def get_is_in_shopping_cart(self, recipe) -> bool:
        request = self.context.get('request')
        return (
                request is not None
                and request.user.is_authenticated
                and ShoppingCart.objects.filter(
            user=request.user.id, recipe=recipe
        ).exists()
        )


class RecipebookInRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    
    class Meta:
        model = Recipebook
        fields = ('id', 'amount')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = RecipebookInRecipeCreateSerializer(
        many=True,
        
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    
    class Meta:
        model = Recipe
        fields = (
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )
    
    def to_representation(self, instance):
        return RecipeReadSerializer().to_representation(instance)
    
    def create(self, validated_data):
        print(f'{validated_data=}')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        user = self.context['request'].user
        if user.is_authenticated:
            instance = Recipe.objects.create(author=user, **validated_data)
            if tags is not None:
                instance.tags.set(tags)
            instance.save()
            batch = []
            for ingredient in ingredients:
                batch.append(
                    Recipebook(
                        ingredient=ingredient['id'],
                        recipe_id=instance.id,
                        amount=ingredient['amount']
                    )
                )
            Recipebook.objects.bulk_create(batch)
            return instance
    
    def update(self, instance, validated_data):
        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')
        
        if tags is None:
            raise serializers.ValidationError('Tags are required')
        if ingredients is None:
            raise serializers.ValidationError('Ingredients are required')

        request = self.context.get('request', None)
        if request is None:
            raise serializers.ValidationError('Bad Error occurs')
        if instance.author != request.user:
            raise PermissionDenied('You cannot edit this recipe')
        instance.tags.clear()
        if tags is not None:
            serializers.ValidationError('Tags must be in recipe')
        instance.tags.set(tags)
        Recipebook.objects.filter(recipe=instance).all().delete()
        batch = []
        for ingredient in ingredients:
            batch.append(Recipebook(
                ingredient=ingredient['id'],
                recipe_id=instance.id,
                amount=ingredient['amount']))
        Recipebook.objects.bulk_create(batch)
        validated_data.pop('ingredients')
        super().update(instance, validated_data)
        return instance
    

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError('Image must be in recipe')
        return image
    
    def validate_tags(self, tags):
        if tags is None or len(tags) == 0:
            raise serializers.ValidationError('Tags must be in recipe')
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError('Tags unique')

        return tags
    
    def validate_ingredients(self, ingredients):
        if len(ingredients) == 0:
            raise serializers.ValidationError(
                'At least one ingredient is required for the recipe'
            )
        ingredient_list = set()
        for ingredient_item in ingredients:
            ingredient = ingredient_item['id']
            if ingredient in ingredient_list:
                raise serializers.ValidationError('Ingredients should be unique')
            ingredient_list.add(ingredient)
        return ingredients
    

class ShortRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор для избранного в рецептах. """
    image = serializers.ImageField(use_url=True)
    
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class RecipeSubscriptionSerializer(serializers.ModelSerializer):
    """ Сериализатор для подписок. """
    name = serializers.CharField(
        max_length=RecipeMaxLength.NAME
    )
    image = Base64ImageField(use_url=True)
    
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        
        if 'limit_fields' in self.context:
            limited_fields = self.context['limit_fields']
            ret = {
                field: ret[field]
                for field in limited_fields
                if field in ret
            }
        
        return ret
