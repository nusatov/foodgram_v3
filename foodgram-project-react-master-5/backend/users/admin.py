from django.contrib import admin
from django.contrib.auth import get_user_model, admin as auth_admin

from .models import Subscription

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    """Класс пользователей для админки."""

    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'is_user_subscribed',
    ]

    search_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
    ]

    list_filter = [
        'username',
        'email',
    ]

    empty_value_display = '-пусто-'

    def is_user_subscribed(self, obj):
        return Subscription.objects.filter(author=obj).exists()
    is_user_subscribed.short_description = 'Подписан'


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    """Класс подписок для админки."""

    list_display = [
        'follower',
        'author',
    ]

    search_fields = [
        'follower',
        'author',
    ]
