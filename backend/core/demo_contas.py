"""Contas de demonstração (tenant gabinete_demo) — dev local."""

from __future__ import annotations

from usuarios.models import Perfil, Permissao, User
from usuarios.serializers import _aplicar_nome, _sincronizar_status_ativo

DEV_SENHA_PADRAO = 'demo123456'

CONTAS_DEMO: list[dict] = [
    {
        'username': 'admin',
        'email': 'admin@demo.localhost',
        'nome': 'Administrador Demo',
        'perfil_nome': 'Administrador',
        'is_staff': True,
        'is_superuser': True,
    },
    {
        'username': 'chefe',
        'email': 'chefe@teste.com',
        'nome': 'Chefe Demo',
        'perfil_nome': 'Chefe de Gabinete',
    },
    {
        'username': 'assessor',
        'email': 'assessor@teste.com',
        'nome': 'Assessor Demo',
        'perfil_nome': 'Assessor Parlamentar',
    },
    {
        'username': 'recepcao',
        'email': 'recepcao@teste.com',
        'nome': 'Recepção Demo',
        'perfil_nome': 'Recepção',
    },
    {
        'username': 'cerimonia',
        'email': 'cerimonia@teste.com',
        'nome': 'Cerimonial Demo',
        'perfil_nome': 'Cerimonialista',
    },
]

_CERIMONIALISTA_PERMS = (
    'ler_crm',
    'ler_agenda',
    'criar_agenda',
    'ler_eventos',
    'criar_eventos',
    'gerenciar_convidados',
    'disparar_comunicacao',
    'ler_docs',
    'view_dashboard_operacional',
)


def garantir_perfil_cerimonialista() -> Perfil:
    perfil, _ = Perfil.objects.get_or_create(
        nome='Cerimonialista',
        defaults={
            'cor': '#8b5cf6',
            'icone': 'calendar-heart',
            'descricao': 'Operação de eventos e cerimonial',
            'is_admin': False,
        },
    )
    permissoes = list(
        Permissao.objects.filter(codename__in=_CERIMONIALISTA_PERMS),
    )
    if permissoes:
        perfil.permissoes.set(permissoes)
    return perfil


def sincronizar_contas_demo(senha: str = DEV_SENHA_PADRAO) -> list[str]:
    """Cria/atualiza usuários demo; retorna lista de e-mails."""
    garantir_perfil_cerimonialista()
    emails: list[str] = []

    for conta in CONTAS_DEMO:
        perfil = Perfil.objects.filter(nome=conta['perfil_nome']).first()
        if perfil is None:
            raise RuntimeError(f'Perfil "{conta["perfil_nome"]}" não encontrado. Rode seed_rbac antes.')

        user, _ = User.objects.update_or_create(
            username=conta['username'],
            defaults={
                'email': conta['email'].strip().lower(),
                'is_staff': conta.get('is_staff', False),
                'is_superuser': conta.get('is_superuser', False),
                'is_active': True,
                'status': User.Status.ATIVO,
                'perfil': perfil,
            },
        )
        _aplicar_nome(user, conta['nome'])
        user.set_password(senha)
        _sincronizar_status_ativo(user)
        user.save()
        emails.append(user.email)

    return emails
