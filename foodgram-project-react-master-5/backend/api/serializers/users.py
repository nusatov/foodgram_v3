from rest_framework import serializers
from rest_framework.validators import UniqueValidator

import api.serializers.recipes as recipes_serializers
from users.models import Subscription, User


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
        return bool(
            request
            and request.user.is_authenticated
            and Subscription.objects.filter(
                follower=request.user,
                author=obj
            ).exists()
        )


class SubscriptionSerializer(UserReadSerializer):
    """ Сериализатор для чтения подписок. """
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = UserReadSerializer.Meta.fields + ('recipes_count', 'recipes')
    
    def get_recipes_count(self, obj):
        return obj.recipes.count()
    
    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit is not None:
            recipes_limit = int(recipes_limit)
            recipes = recipes[:recipes_limit]
        return recipes_serializers.RecipeSubscriptionSerializer(
            recipes, many=True,
            context=self.context
        ).data
    
