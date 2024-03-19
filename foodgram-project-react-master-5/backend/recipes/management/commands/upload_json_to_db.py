import json
import os
from pathlib import Path

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузите список ингредиентов из файла JSON в базу данных. (data/ingredients.json)'

    def handle(self, *args, **kwargs):
        json_file = 'data/ingredients.json'
        with open(json_file, encoding='utf-8') as file:
            data = json.load(file)

            ingredients = [
                Ingredient(
                    name=entry['name'],
                    measurement_unit=entry['measurement_unit']
                )
                for entry in data
            ]

            Ingredient.objects.bulk_create(ingredients)

        self.stdout.write(self.style.SUCCESS(
            'Ингредиенты успешно загружены.')
        )
