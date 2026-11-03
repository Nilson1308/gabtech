from rest_framework.permissions import BasePermission


def _usuario_tem_codename(user, codename: str) -> bool:
    if getattr(user, 'tem_acesso_total', False):
        return True
    return codename in user.get_permissao_codenames()


class CanManageProfiles(BasePermission):
    """Administrador do tenant ou permissão ``manage_profiles``."""

    message = 'Você não tem permissão para gerenciar perfis RBAC.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return _usuario_tem_codename(user, 'manage_profiles')


class CanListPerfisRBAC(BasePermission):
    """Listar perfis: quem gerencia usuários ou a matriz RBAC."""

    message = 'Você não tem permissão para visualizar perfis.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, 'tem_acesso_total', False):
            return True
        codenames = user.get_permissao_codenames()
        return 'manage_profiles' in codenames or 'manage_users' in codenames


class CanManageUsers(BasePermission):
    """Administrador do tenant ou permissão ``manage_users``."""

    message = 'Você não tem permissão para gerenciar usuários.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, 'tem_acesso_total', False):
            return True
        return 'manage_users' in user.get_permissao_codenames()


class ActionRBACPermission(BasePermission):
    """
    Checa codename RBAC definido em ViewSet.get_rbac_codename() por action.
    """

    message = 'Você não tem permissão para executar esta ação.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        codename = getattr(view, 'get_rbac_codename', lambda: None)()
        if not codename:
            return True

        return codename in user.get_permissao_codenames()
