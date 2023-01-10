from rest_framework import permissions

from users.models import ADMIN


class AuthorOrAdminOrReadOnly(permissions.BasePermission):
    """Кастомный пермишен для доступка к редактированию объекта.

    Доступ только для его автора или администратора.
    """

    message = 'Редактирование доступно только автору или администратору'

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS or
            request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.role == ADMIN
