from django.db import models

from django.contrib.auth.models import AbstractUser

USER = 'user'
ADMIN = 'admin'
ROLE_CHOICES = [(USER, 'user'), (ADMIN, 'admin')]

class User(AbstractUser):
    first_name = models.CharField('имя', max_length=150)
    last_name = models.CharField('фамилия', max_length=150)
    email = models.EmailField('email', max_length=254)
    role = models.CharField(verbose_name='роль', default=USER, choices=ROLE_CHOICES, max_length=20)
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

