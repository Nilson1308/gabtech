"""Escopo de visualização de atendimentos por permissão RBAC."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import QuerySet

from .models import Atendimento

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser

PERMISSAO_VER_TODOS_ATENDIMENTOS = 'ver_todos_atend'


def usuario_ve_todos_atendimentos(user: AbstractBaseUser) -> bool:
    if getattr(user, 'tem_acesso_total', False):
        return True
    return PERMISSAO_VER_TODOS_ATENDIMENTOS in user.get_permissao_codenames()


def filtrar_atendimentos_visiveis(
    queryset: QuerySet[Atendimento],
    user: AbstractBaseUser,
) -> QuerySet[Atendimento]:
    if usuario_ve_todos_atendimentos(user):
        return queryset
    return queryset.filter(responsavel=user)


def usuario_pode_acessar_atendimento(user: AbstractBaseUser, atendimento: Atendimento) -> bool:
    if usuario_ve_todos_atendimentos(user):
        return True
    return atendimento.responsavel_id == user.pk


def aplicar_escopo_atendimento_em_serializer(serializer) -> None:
    """Restringe FKs de atendimento/despacho nos serializers de escrita."""
    from rest_framework.relations import PrimaryKeyRelatedField

    request = serializer.context.get('request')
    if not request or not getattr(request.user, 'is_authenticated', False):
        return

    visiveis = filtrar_atendimentos_visiveis(Atendimento.objects.all(), request.user)
    for nome in ('atendimento', 'atendimento_id'):
        campo = serializer.fields.get(nome)
        if isinstance(campo, PrimaryKeyRelatedField):
            campo.queryset = visiveis

    from .models import Despacho

    campo_despacho = serializer.fields.get('despacho')
    if isinstance(campo_despacho, PrimaryKeyRelatedField):
        campo_despacho.queryset = Despacho.objects.filter(atendimento__in=visiveis)
