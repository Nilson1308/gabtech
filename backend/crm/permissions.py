from rest_framework.permissions import BasePermission

MODULOS_TAG_VALIDOS = frozenset({'crm', 'atendimentos'})


def normalizar_modulos_tag(raw) -> list[str]:
    if not isinstance(raw, list):
        return ['crm']
    out: list[str] = []
    for item in raw:
        key = str(item).strip()
        if key in MODULOS_TAG_VALIDOS and key not in out:
            out.append(key)
    return out or ['crm']


class CidadaoListAccessPermission(BasePermission):
    """Listagem/busca de cidadãos — CRM, agenda, atendimentos ou convidados."""

    message = 'Você não tem permissão para consultar cidadãos.'

    CODENAMES = frozenset(
        {
            'ler_crm',
            'criar_crm',
            'ler_agenda',
            'criar_agenda',
            'gerenciar_convidados',
            'ler_atend',
            'criar_atend',
            'ler_servicos',
            'gerenciar_talentos',
            'gerenciar_assistencia',
            'gerenciar_cursos',
            'disparar_comunicacao',
        },
    )

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, 'tem_acesso_total', False):
            return True
        perms = set(user.get_permissao_codenames())
        return bool(perms & self.CODENAMES)


class TagRBACPermission(BasePermission):
    """Tags CRM: leitura compartilhada; criação em atendimentos com criar_atend."""

    message = 'Você não tem permissão para gerenciar tags.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if getattr(user, 'tem_acesso_total', False):
            return True

        perms = user.get_permissao_codenames()
        action = getattr(view, 'action', None)

        if action in ('list', 'retrieve'):
            return (
                'ler_crm' in perms
                or 'ler_atend' in perms
                or 'disparar_comunicacao' in perms
                or 'gerenciar_convidados' in perms
                or 'manage_tags' in perms
                or 'ler_eventos' in perms
            )

        if action == 'create':
            if 'manage_tags' in perms:
                return True
            modulos = normalizar_modulos_tag(request.data.get('modulos'))
            if modulos == ['atendimentos'] and 'criar_atend' in perms:
                return True
            return False

        if action in ('update', 'partial_update', 'destroy'):
            return 'manage_tags' in perms

        return False
