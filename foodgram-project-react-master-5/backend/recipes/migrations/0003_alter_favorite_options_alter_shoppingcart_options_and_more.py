# Generated by Django 4.2.7 on 2024-03-19 10:30

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import foodgram_backend.enum


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("recipes", "0002_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="favorite",
            options={
                "default_related_name": "favorites",
                "verbose_name": "Избранный рецепт",
                "verbose_name_plural": "Избранные рецепты",
            },
        ),
        migrations.AlterModelOptions(
            name="shoppingcart",
            options={
                "default_related_name": "shopping_carts",
                "verbose_name": "Рецепт в корзине",
                "verbose_name_plural": "Рецепты в корзине",
            },
        ),
        migrations.AlterField(
            model_name="recipe",
            name="cooking_time",
            field=models.PositiveSmallIntegerField(
                help_text="Необходимо указать время приготовления в минутах",
                validators=[
                    django.core.validators.MinValueValidator(
                        foodgram_backend.enum.RecipeCookingTime["MIN"]
                    )
                ],
                verbose_name="Время приготовления в минутах",
            ),
        ),
        migrations.AlterField(
            model_name="recipebook",
            name="amount",
            field=models.PositiveSmallIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(
                        foodgram_backend.enum.RecipeAmount["MIN"]
                    )
                ],
                verbose_name="Количество",
            ),
        ),
        migrations.AlterField(
            model_name="shoppingcart",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="recipes.recipe",
                verbose_name="Рецепт",
            ),
        ),
        migrations.AlterField(
            model_name="shoppingcart",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Пользователь",
            ),
        ),
    ]
