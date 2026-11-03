from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from usuarios.models import User


def obter_perfil_administrador():
    from usuarios.models import Perfil

    return (
        Perfil.objects.filter(is_admin=True).order_by('pk').first()
        or Perfil.objects.filter(nome='Administrador').order_by('pk').first()
    )


def vincular_perfil_administrador(user: User) -> bool:
    """
    Atribui o perfil Administrador a superusuários sem perfil RBAC.
    Retorna True se o vínculo foi aplicado.
    """
    if not user.is_superuser or user.perfil_id:
        return False

    perfil = obter_perfil_administrador()
    if perfil is None:
        return False

    from usuarios.models import User

    User.objects.filter(pk=user.pk).update(perfil_id=perfil.pk)
    user.perfil_id = perfil.pk
    user.perfil = perfil
    return True


def vincular_superusers_sem_perfil() -> int:
    from usuarios.models import User

    atualizados = 0
    for user in User.objects.filter(is_superuser=True, perfil__isnull=True):
        if vincular_perfil_administrador(user):
            atualizados += 1
    return atualizados
