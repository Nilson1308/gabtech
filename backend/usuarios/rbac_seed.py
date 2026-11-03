"""Seed RBAC reutilizável (CLI, provisionamento de tenant, etc.)."""

from __future__ import annotations

from django.db import transaction

from usuarios.models import Modulo, Perfil, Permissao
from usuarios.rbac_seed_data import MODULOS, PERFIS
from usuarios.rbac_utils import vincular_superusers_sem_perfil


def sincronizar_modulos_e_permissoes() -> dict[str, Permissao]:
    permissoes_map: dict[str, Permissao] = {}

    for modulo_data in MODULOS:
        modulo, _ = Modulo.objects.update_or_create(
            codename=modulo_data['codename'],
            defaults={
                'nome': modulo_data['nome'],
                'icone': modulo_data['icone'],
                'cor': modulo_data['cor'],
            },
        )

        for perm_data in modulo_data['permissoes']:
            permissao, _ = Permissao.objects.update_or_create(
                codename=perm_data['codename'],
                defaults={
                    'nome': perm_data['nome'],
                    'descricao': perm_data['descricao'],
                    'modulo': modulo,
                },
            )
            permissoes_map[permissao.codename] = permissao

    return permissoes_map


def sincronizar_perfis_padrao(permissoes_map: dict[str, Permissao]) -> int:
    for perfil_data in PERFIS:
        perfil, _ = Perfil.objects.update_or_create(
            nome=perfil_data['nome'],
            defaults={
                'cor': perfil_data['cor'],
                'icone': perfil_data['icone'],
                'descricao': perfil_data['descricao'],
                'is_admin': perfil_data['is_admin'],
            },
        )

        codenames = perfil_data['permissoes']
        missing = [code for code in codenames if code not in permissoes_map]
        if missing:
            raise ValueError(f'Permissões ausentes no catálogo: {", ".join(missing)}')

        perfil.permissoes.set([permissoes_map[code] for code in codenames])

    return len(PERFIS)


@transaction.atomic
def executar_seed_rbac() -> tuple[int, int, int]:
    """
    Executa seed completo no schema atual (use dentro de schema_context).
    Retorna (qtd_permissoes, qtd_perfis, superusers_vinculados).
    """
    permissoes_map = sincronizar_modulos_e_permissoes()
    perfis = sincronizar_perfis_padrao(permissoes_map)
    superusers = vincular_superusers_sem_perfil()
    return len(permissoes_map), perfis, superusers
