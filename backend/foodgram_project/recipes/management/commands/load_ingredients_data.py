from csv import DictReader
from pathlib import Path

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    print('Загрузка данных из ingredients.csv')

    def handle(self, *args, **kwargs):
            with open(
                '../../data/ingredients.csv',
                'r', encoding='utf-8'
            ) as csv_file:
                reader = DictReader(csv_file)
                for item in reader:
                    Ingredient.objects.create(name=item['name'], measurment_unit=item['measurment_unit'])
                print('Данные успешно загружены в базу данных')

    