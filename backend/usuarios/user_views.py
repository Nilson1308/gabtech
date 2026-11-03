from django.contrib.auth import get_user_model
from config.viewsets import GabineteModelViewSet
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from usuarios.models import Perfil
from usuarios.permissions import CanListPerfisRBAC, CanManageProfiles, CanManageUsers
from usuarios.serializers import PerfilSerializer, UsuarioSerializer

User = get_user_model()


class PerfilViewSet(GabineteModelViewSet):
    """
    CRUD de perfis RBAC (/api/perfis/).

    GET: manage_users ou manage_profiles.
    POST/PATCH/DELETE: manage_profiles.
    """

    queryset = Perfil.objects.prefetch_related('permissoes').order_by('nome')
    serializer_class = PerfilSerializer
    pagination_class = None
    http_method_names = ['get', 'post', 'patch', 'put', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated(), CanListPerfisRBAC()]
        return [IsAuthenticated(), CanManageProfiles()]

    def perform_destroy(self, instance):
        if instance.is_admin:
            raise ValidationError('O perfil Administrador não pode ser excluído.')
        if instance.usuarios.exists():
            raise ValidationError(
                'Este perfil está vinculado a usuários. Reatribua-os antes de excluir.',
            )
        super().perform_destroy(instance)


class UsuarioViewSet(GabineteModelViewSet):
    """CRUD de usuários da equipe (/api/usuarios/)."""

    queryset = User.objects.select_related('perfil').order_by('first_name', 'last_name', 'email')
    serializer_class = UsuarioSerializer
    permission_classes = (IsAuthenticated, CanManageUsers)
    pagination_class = None
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']

    def perform_destroy(self, instance):
        """Inativa em vez de remover registro (preserva integridade referencial)."""
        instance.status = User.Status.INATIVO
        instance.is_active = False
        instance.save(update_fields=['status', 'is_active'])
