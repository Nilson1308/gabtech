"""
Motor de matchmaking por interseção de tags (crm.Tag).
"""

from __future__ import annotations

from dataclasses import dataclass

from django.db.models import Count, Q, Value, IntegerField
from django.db.models.functions import Coalesce

from crm.models import Cidadao, DocumentoAnexo, Tag


@dataclass
class SugestaoMatch:
    cidadao: Cidadao
    score: int
    tags: list[Tag]


def _tags_resumo(tags: list[Tag]) -> list[Tag]:
    return sorted(tags, key=lambda t: t.nome.lower())


def _coletar_tags_cidadao(cidadao: Cidadao) -> set[int]:
    ids: set[int] = set(cidadao.marcadores.values_list('id', flat=True))
    for doc in cidadao.documentos.filter(categoria=DocumentoAnexo.Categoria.CURRICULO):
        ids.update(doc.etiquetas.values_list('id', flat=True))
    for perfil in cidadao.perfis_profissionais.select_related('tag'):
        if perfil.tag_id:
            ids.add(perfil.tag_id)
    return ids


def sugerir_candidatos_para_vaga(vaga, limit: int = 50) -> list[SugestaoMatch]:
    """Currículo obrigatório + interseção com tags_alvo da vaga (se houver)."""
    target_ids = list(vaga.tags_alvo.values_list('id', flat=True))
    tag_map = {t.id: t for t in Tag.objects.filter(id__in=target_ids)} if target_ids else {}

    qs = Cidadao.objects.select_related('endereco').filter(
        documentos__categoria=DocumentoAnexo.Categoria.CURRICULO,
    )
    if target_ids:
        qs = qs.filter(
            documentos__categoria=DocumentoAnexo.Categoria.CURRICULO,
            documentos__etiquetas__id__in=target_ids,
        )
        qs = qs.annotate(
            score=Count(
                'documentos__etiquetas',
                filter=Q(
                    documentos__categoria=DocumentoAnexo.Categoria.CURRICULO,
                    documentos__etiquetas__id__in=target_ids,
                ),
                distinct=True,
            ),
        )
    else:
        qs = qs.annotate(score=Coalesce(Value(0), Value(0), output_field=IntegerField()))

    qs = qs.distinct().order_by('-score', 'nome')[:limit]

    out: list[SugestaoMatch] = []
    for cidadao in qs:
        score = int(getattr(cidadao, 'score', 0) or 0)
        if target_ids:
            cidadao_tag_ids = _coletar_tags_cidadao(cidadao)
            overlap = [tag_map[i] for i in target_ids if i in cidadao_tag_ids and i in tag_map]
        else:
            overlap = []
        out.append(SugestaoMatch(cidadao=cidadao, score=score, tags=_tags_resumo(overlap)))
    return out


def sugerir_publico_por_tags(
    tags_alvo,
    *,
    limit: int = 50,
    exigir_curriculo: bool = False,
) -> list[SugestaoMatch]:
    """Público elegível por marcadores, currículo ou perfil profissional (sem exigir currículo por padrão)."""
    target_ids = list(tags_alvo.values_list('id', flat=True))
    if not target_ids:
        qs = Cidadao.objects.select_related('endereco').order_by('nome')[:limit]
        return [SugestaoMatch(cidadao=c, score=0, tags=[]) for c in qs]

    tag_map = {t.id: t for t in Tag.objects.filter(id__in=target_ids)}

    qs = Cidadao.objects.select_related('endereco').prefetch_related(
        'marcadores',
        'documentos__etiquetas',
        'perfis_profissionais__tag',
    )
    if exigir_curriculo:
        qs = qs.filter(documentos__categoria=DocumentoAnexo.Categoria.CURRICULO)

    candidatos: list[SugestaoMatch] = []
    for cidadao in qs.distinct():
        cidadao_tags = _coletar_tags_cidadao(cidadao)
        overlap_ids = [tid for tid in target_ids if tid in cidadao_tags]
        if not overlap_ids:
            continue
        overlap_tags = [tag_map[i] for i in overlap_ids if i in tag_map]
        candidatos.append(
            SugestaoMatch(
                cidadao=cidadao,
                score=len(overlap_ids),
                tags=_tags_resumo(overlap_tags),
            ),
        )

    candidatos.sort(key=lambda s: (-s.score, s.cidadao.nome.lower()))
    return candidatos[:limit]
