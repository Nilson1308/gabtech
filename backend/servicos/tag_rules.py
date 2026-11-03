"""Regras de tags CRM usadas pelo módulo Serviços (sem módulo «servicos» nas tags)."""

from rest_framework import serializers

from crm.models import Tag

TIPOS_CONTEXTO_PROFISSIONAL = frozenset(
    {
        Tag.Tipo.CONTEXTO_PROFISSIONAL,
    },
)

TIPOS_SEGMENTACAO = frozenset(
    {
        Tag.Tipo.SEGMENTACAO,
        Tag.Tipo.AMBOS,
    },
)


def _tag_no_crm(tag: Tag) -> bool:
    modulos = tag.modulos if isinstance(tag.modulos, list) else []
    return 'crm' in modulos or 'atendimentos' in modulos


def validar_tags_contexto_profissional(tags) -> list:
    for tag in tags:
        if not _tag_no_crm(tag):
            raise serializers.ValidationError(
                f'A etiqueta «{tag.nome}» precisa estar disponível no CRM.',
            )
        if tag.tipo not in TIPOS_CONTEXTO_PROFISSIONAL:
            raise serializers.ValidationError(
                f'A etiqueta «{tag.nome}» deve ser do tipo Contexto profissional '
                f'(vagas, cursos e currículos).',
            )
    return tags


def validar_tags_segmentacao(tags) -> list:
    for tag in tags:
        if not _tag_no_crm(tag):
            raise serializers.ValidationError(
                f'A etiqueta «{tag.nome}» precisa estar disponível no CRM.',
            )
        if tag.tipo not in TIPOS_SEGMENTACAO:
            raise serializers.ValidationError(
                f'A etiqueta «{tag.nome}» deve ser de Segmentação '
                f'(ex.: PCD, baixa renda — assistência social).',
            )
    return tags
