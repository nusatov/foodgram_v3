from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Загрузите список ингредиентов из файла JSON в базу данных.'

    def handle(self, *args, **kwargs):
        Ingredient.objects.create(name='Тыква', measurement_unit='г')
        Ingredient.objects.create(name='Sugar', measurement_unit='г')
        Ingredient.objects.create(name='Honey', measurement_unit='г')
        Tag.objects.create(name='First', color='red', slug='first')
        Tag.objects.create(name='Second', color='blue', slug='second')
        Tag.objects.create(name='Third', color='black', slug='third')
        self.stdout.write(self.style.SUCCESS(
            'Database populated successfully!')
        )
