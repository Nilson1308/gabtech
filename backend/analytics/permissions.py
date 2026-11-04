from rest_framework.permissions import BasePermission

from usuarios.permissions import _usuario_tem_codename


def codename_permission(codename: str):
    class _Perm(BasePermission):
        message = 'Você não tem permissão para acessar este recurso.'

        def has_permission(self, request, view):
            user = request.user
            if not user or not user.is_authenticated:
                return False
            return _usuario_tem_codename(user, codename)

    _Perm.__name__ = f'Requires_{codename}'
    return _Perm


def codename_permission_any(*codenames: str):
    class _PermAny(BasePermission):
        message = 'Você não tem permissão para acessar este recurso.'

        def has_permission(self, request, view):
            user = request.user
            if not user or not user.is_authenticated:
                return False
            return any(_usuario_tem_codename(user, c) for c in codenames)

    _PermAny.__name__ = 'Requires_dashboard_any'
    return _PermAny
