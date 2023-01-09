from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Кастомный класс для администрирования модели Юзер."""

    search_fields = ('email', 'username',)
