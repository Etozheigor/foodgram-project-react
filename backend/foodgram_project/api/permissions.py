from rest_framework import permissions


class AuthorOrAdminOrReadOnly(permissions.BasePermission):
    message = 'Редактирование доступно только автору рецепта или администратору'
    
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.role == 'admin'
 

class AdminOnly(permissions.BasePermission):
    message = 'Доступно только администраторам'
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'