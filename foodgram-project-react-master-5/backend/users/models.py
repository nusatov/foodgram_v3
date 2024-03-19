from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from foodgram_backend.enum import UserMaxLength


class User(AbstractUser):
    """Класс пользователей."""
    
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=UserMaxLength.USERNAME,
        unique=True,
        validators=[UnicodeUsernameValidator()]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=UserMaxLength.FIRST_NAME.value,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=UserMaxLength.LAST_NAME.value,
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
        max_length=UserMaxLength.EMAIL.value,
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')
    
    class Meta:
        ordering = ('username', 'email')
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписок."""
    
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписчик',
        help_text='Необходимо указать подписчика'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bloger',
        verbose_name='Блогер',
        help_text='Необходимо указать блогера'
    )
    
    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.CheckConstraint(
                check=~models.Q(follower=models.F('author')),
                name='not_self_subscribe',
            ),
            models.UniqueConstraint(
                fields=['follower', 'author'],
                name='unique_subscribe',
            )
        ]
    
    def __str__(self):
        return f'Ваша подписка: {self.follower} на {self.author} осуществлена'
