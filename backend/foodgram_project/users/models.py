from django.db import models

from django.contrib.auth.models import AbstractUser

USER = 'user'
ADMIN = 'admin'
ROLE_CHOICES = [(USER, 'user'), (ADMIN, 'admin')]

class User(AbstractUser):
    email = models.EmailField(verbose_name='email address', blank=True, max_length=254)
    first_name = models.CharField(verbose_name='имя', blank=True, max_length=150)
    last_name = models.CharField(verbose_name='фамилия', blank=True, max_length=150)
    username = models.CharField(verbose_name='username', blank=True, max_length=150, unique=True)
    password = models.CharField(verbose_name='пароль', blank=True, max_length=150)
    role = models.CharField(verbose_name='роль', default=USER, choices=ROLE_CHOICES)

