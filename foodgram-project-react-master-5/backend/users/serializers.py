from rest_framework import serializers
from rest_framework.validators import UniqueValidator

import recipes.serializers as recipes_serializers
from .models import Subscription, User


class UserReadSerializer(serializers.ModelSerializer):
    """ Сериализатор для чтения данных пользователя. """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed'
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                follower=request.user,
                author=obj
            ).exists()
        return False


class SubscriptionSerializer(UserReadSerializer):
    """ Сериализатор для чтения подписок. """
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(UserReadSerializer.Meta):
        fields = UserReadSerializer.Meta.fields + ('recipes_count', 'recipes')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit is not None:
            recipes_limit = int(recipes_limit)
            recipes = recipes[:recipes_limit]
        return recipes.serializers.RecipeSubscriptionSerializer(
            recipes, many=True,
            context=self.context
        ).data


class UserFollowSerializer(serializers.ModelSerializer):
    """
    Пользовательский сериализатор для модели User.
    Расширяет стандартный сериализатор Djoser, добавляя дополнительные поля.
    """
    username = serializers.CharField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="Ничего у тебя не получится")]
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes_count',
            'recipes'
        )

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        if 'is_subscription_request' in self.context:
            if recipes_limit is not None:
                recipes = obj.recipes.all()[:recipes_limit]
            else:
                recipes = obj.recipes.all()

            return recipes_serializers.RecipeSubscriptionSerializer(
                recipes, many=True, context=self.context
            ).data
        else:
            return recipes_serializers.RecipeCreateUpdateSerializer(
                obj.recipes.all(), many=True, context=self.context
            ).data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                follower=request.user, author=obj
            ).exists()
        return False

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if self.context.get('include_extra_fields', False):
            recipes_limit = self.context.get('recipes_limit')
            if recipes_limit is not None:
                recipes = instance.recipes.all()[:recipes_limit]
            else:
                recipes = instance.recipes.all()

            ret['recipes_count'] = len(recipes)
            ret['recipes'] = recipes.serializers.RecipeCreateUpdateSerializer(
                recipes, many=True, context=self.context
            ).data
        return ret

    def get_recipes_count(self, obj):
        return obj.recipes.count()
