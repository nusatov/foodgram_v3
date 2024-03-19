import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузите список ингредиентов из файла JSON в базу данных.'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Файл JSON для загрузки.'
        )

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']
        with open(json_file, 'r', encoding='utf-8') as file:
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
