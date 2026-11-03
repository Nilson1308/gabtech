"""Agregações leves para o dashboard operacional (sem listar todos os atendimentos)."""

from __future__ import annotations

from typing import Any

from django.db.models import Count, Q
from django.utils import timezone

from crm.models import Tag

from .models import Atendimento
from .serializers import AtendimentoKanbanSerializer
from .visibility import filtrar_atendimentos_visiveis


def _qs_visivel(user):
    return filtrar_atendimentos_visiveis(
        Atendimento.objects.select_related('macrotema', 'cidadao', 'responsavel'),
        user,
    )


def build_dashboard_resumo(user) -> dict[str, Any]:
    agora = timezone.now()
    qs = _qs_visivel(user)

    abertos = qs.exclude(status=Atendimento.Status.CONCLUIDO).count()
    sla_atrasados = (
        qs.exclude(status=Atendimento.Status.CONCLUIDO)
        .filter(sla_vencimento__isnull=False, sla_vencimento__lt=agora)
        .count()
    )

    por_macrotema = (
        qs.values('macrotema__nome', 'macrotema__cor')
        .annotate(quantidade=Count('id'))
        .order_by('-quantidade')
    )
    macrotemas = [
        {
            'macrotema': row['macrotema__nome'] or '—',
            'cor': row['macrotema__cor'] or '#6b7280',
            'quantidade': row['quantidade'],
        }
        for row in por_macrotema
    ]

    recentes_qs = qs.order_by('-created_at')[:5]
    recentes = AtendimentoKanbanSerializer(recentes_qs, many=True).data

    top_tags_qs = (
        Tag.objects.filter(atendimentos__in=qs)
        .values('id', 'nome', 'cor', 'tipo', 'modulos')
        .annotate(count=Count('atendimentos', distinct=True))
        .order_by('-count')[:5]
    )
    top_tags = [
        {
            'tag': {
                'id': row['id'],
                'nome': row['nome'],
                'cor': row['cor'],
                'tipo': row['tipo'],
                'modulos': row['modulos'],
            },
            'count': row['count'],
        }
        for row in top_tags_qs
    ]

    return {
        'abertos': abertos,
        'sla_atrasados': sla_atrasados,
        'total_atendimentos': qs.count(),
        'por_macrotema': macrotemas,
        'recentes': recentes,
        'top_tags': top_tags,
    }
