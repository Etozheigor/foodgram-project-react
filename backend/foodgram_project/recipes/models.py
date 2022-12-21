from django.db import models
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(verbose_name= 'Название', blank=True, max_length=200)
    measurment_unit = models.CharField(verbose_name='Единица измерения', blank=True, max_length=200)

class Tag(models.Model):
    name = models.CharField(verbose_name= 'Название', blank=True, max_length=200)
    color = models.CharField(verbose_name='Цвет в HEX', null=True, max_length=7)
    slug = models.SlugField(verbose_name='Уникальный слаг', null=True, max_length=200)

class Recipe(models.Model):
    text = models.TextField(verbose_name='Описание', blank=True)
    name = models.CharField(verbose_name='Название', blank=True, max_length=200)
    cooking_time = models.PositiveSmallIntegerField(verbose_name='Время приготовления (в минутах)')
