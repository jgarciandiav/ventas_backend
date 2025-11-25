# core/permissions.py

from rest_framework import permissions
from .models import User  # ← IMPORTANTE: sin esto, 'User' no existe


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'administrador'


class IsAdminOrAlmacenero(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in ['administrador', 'almacenero']


class CanUpdatePrecio(permissions.BasePermission):
    def has_permission(self, request, view):
        if 'precio' not in request.data:
            return True
        return request.user.is_authenticated and request.user.rol == 'administrador'


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, User):  # ← ahora 'User' está definido
            return obj == request.user or request.user.rol == 'administrador'
        return request.user.rol == 'administrador'   