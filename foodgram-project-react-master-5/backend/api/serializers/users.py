from rest_framework import serializers, status

import api.serializers.recipes as recipes_serializers
from recipes.models import Recipe
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
        recipes_limit = self.context.get('request').GET.get('recipes_limit')
        print(f'recipes_limit: {recipes_limit}')
        print(f'{obj=}')
        recipes = Recipe.objects.filter(author=obj)
        print(f'{recipes=}')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return recipes_serializers.RecipeSubscriptionSerializer(
            recipes, many=True,
            context=self.context
        ).data


class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('follower', 'author')
    
    def validate(self, data):
        if data['follower'] == data['author']:
            raise serializers.ValidationError(
                'You cannot subscribe yourself',
                code=status.HTTP_400_BAD_REQUEST
            )
        
        if Subscription.objects.filter(follower=data['follower'], author=data['author']).exists():
            raise serializers.ValidationError(
                'You are already subscribed',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data
    
    def to_representation(self, instance):
        return SubscriptionSerializer(instance.author, context=self.context).data
