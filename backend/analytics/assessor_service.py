"""Métricas de desempenho individual por assessor (gestão)."""

from __future__ import annotations

from datetime import date
from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone

from atendimentos.models import Atendimento, Despacho
from atendimentos.visibility import usuario_ve_todos_atendimentos

from .services import STATUS_LABEL, _atendimentos_visiveis, _is_atrasado

User = get_user_model()

STATUS_UI = {
    'aberto': 'Aberto',
    'em_andamento': 'Em andamento',
    'aguardando_terceiros': 'Aguardando terceiros',
    'concluido': 'Concluído',
}


def _parse_periodo(de: date | None, ate: date | None) -> tuple[date | None, date | None]:
    if de and ate and de > ate:
        return ate, de
    return de, ate


def _aplicar_periodo(qs, de: date | None, ate: date | None):
    if de:
        qs = qs.filter(created_at__date__gte=de)
    if ate:
        qs = qs.filter(created_at__date__lte=ate)
    return qs


def _metricas_resumo(qs, agora) -> dict[str, Any]:
    atrasado_filter = Q(
        ~Q(status=Atendimento.Status.CONCLUIDO),
        sla_vencimento__isnull=False,
        sla_vencimento__lt=agora,
    )
    concluido_filter = Q(status=Atendimento.Status.CONCLUIDO)

    agg = qs.aggregate(
        total=Count('id'),
        concluidos=Count('id', filter=concluido_filter),
        atrasados=Count('id', filter=atrasado_filter),
    )
    total = agg['total'] or 0
    concluidos = agg['concluidos'] or 0
    atrasados = agg['atrasados'] or 0
    em_andamento = total - concluidos
    taxa = round((concluidos / total) * 100, 1) if total else 0.0

    return {
        'total': total,
        'concluidos': concluidos,
        'atrasados': atrasados,
        'em_andamento': em_andamento,
        'taxa_sucesso': taxa,
    }


def build_equipe_desempenho(user) -> dict[str, Any]:
    """Lista assessores com volume (para seletor do gestor)."""
    if not usuario_ve_todos_atendimentos(user):
        alvo = User.objects.filter(pk=user.pk).select_related('perfil').first()
        if not alvo:
            return {'membros': [], 'pode_ver_equipe': False}
        qs = _atendimentos_visiveis(user).filter(responsavel=user)
        resumo = _metricas_resumo(qs, timezone.now())
        return {
            'pode_ver_equipe': False,
            'membros': [
                {
                    'user_id': str(alvo.pk),
                    'nome': alvo.nome,
                    'email': alvo.email,
                    'cargo': alvo.cargo,
                    'avatar': alvo.avatar or '',
                    'total_atendimentos': resumo['total'],
                    'taxa_sucesso': resumo['taxa_sucesso'],
                }
            ],
        }

    agora = timezone.now()
    qs = _atendimentos_visiveis(user)
    atrasado_filter = Q(
        ~Q(status=Atendimento.Status.CONCLUIDO),
        sla_vencimento__isnull=False,
        sla_vencimento__lt=agora,
    )
    concluido_filter = Q(status=Atendimento.Status.CONCLUIDO)

    por_resp = (
        qs.values('responsavel_id')
        .annotate(
            total=Count('id'),
            concluidos=Count('id', filter=concluido_filter),
            atrasados=Count('id', filter=atrasado_filter),
        )
        .order_by('-total')
    )
    resp_ids = [row['responsavel_id'] for row in por_resp if row['responsavel_id']]
    nomes = {
        u.pk: u
        for u in User.objects.filter(pk__in=resp_ids).select_related('perfil')
    }

    membros = []
    for row in por_resp:
        rid = row['responsavel_id']
        if not rid or rid not in nomes:
            continue
        u = nomes[rid]
        total = row['total'] or 0
        concluidos = row['concluidos'] or 0
        taxa = round((concluidos / total) * 100, 1) if total else 0.0
        membros.append(
            {
                'user_id': str(rid),
                'nome': u.nome,
                'email': u.email,
                'cargo': u.cargo,
                'avatar': u.avatar or '',
                'total_atendimentos': total,
                'taxa_sucesso': taxa,
                'atrasados': row['atrasados'] or 0,
            }
        )

    return {'pode_ver_equipe': True, 'membros': membros}


def build_assessor_desempenho(
    user,
    responsavel_id: int,
    *,
    de: date | None = None,
    ate: date | None = None,
) -> dict[str, Any]:
    de, ate = _parse_periodo(de, ate)

    if not usuario_ve_todos_atendimentos(user) and responsavel_id != user.pk:
        return {'detail': 'Sem permissão para analisar outro assessor.'}

    alvo = User.objects.filter(pk=responsavel_id).select_related('perfil').first()
    if not alvo:
        return {'detail': 'Assessor não encontrado.'}

    agora = timezone.now()
    qs = _aplicar_periodo(
        _atendimentos_visiveis(user).filter(responsavel_id=responsavel_id),
        de,
        ate,
    )

    resumo = _metricas_resumo(qs, agora)

    por_status = [
        {
            'status': row['status'],
            'rotulo': STATUS_UI.get(row['status'], row['status']),
            'quantidade': row['c'],
        }
        for row in qs.values('status').annotate(c=Count('id')).order_by('-c')
    ]

    por_macrotema = [
        {
            'macrotema': row['macrotema__nome'] or '—',
            'cor': row['macrotema__cor'] or '#6b7280',
            'quantidade': row['c'],
        }
        for row in qs.values('macrotema__nome', 'macrotema__cor')
        .annotate(c=Count('id'))
        .order_by('-c')
    ]

    recentes = []
    for att in qs.select_related('macrotema', 'cidadao').order_by('-updated_at')[:10]:
        recentes.append(
            {
                'id': att.pk,
                'protocolo': att.protocolo,
                'status': att.status,
                'status_rotulo': STATUS_UI.get(att.status, att.status),
                'macrotema': att.macrotema.nome if att.macrotema else '—',
                'cidadao_nome': att.cidadao.nome if att.cidadao else '—',
                'atrasado': _is_atrasado(att, agora),
                'updated_at': att.updated_at.isoformat(),
            }
        )

    atividades = _atividades_assessor(qs, alvo, agora)

    comparativo = _comparativo_equipe(user, de, ate, resumo['taxa_sucesso'])

    return {
        'assessor': {
            'user_id': str(alvo.pk),
            'nome': alvo.nome,
            'email': alvo.email,
            'cargo': alvo.cargo,
            'avatar': alvo.avatar or '',
        },
        'periodo': {
            'de': de.isoformat() if de else None,
            'ate': ate.isoformat() if ate else None,
        },
        'resumo': resumo,
        'por_status': por_status,
        'por_macrotema': por_macrotema,
        'atendimentos_recentes': recentes,
        'atividades': atividades,
        'comparativo_equipe': comparativo,
    }


def _comparativo_equipe(
    user,
    de: date | None,
    ate: date | None,
    taxa_assessor: float,
) -> dict[str, Any]:
    qs = _aplicar_periodo(_atendimentos_visiveis(user), de, ate)
    agora = timezone.now()
    equipe = _metricas_resumo(qs, agora)
    media = equipe['taxa_sucesso']
    return {
        'taxa_sucesso_media': media,
        'delta_taxa': round(taxa_assessor - media, 1),
        'total_equipe': equipe['total'],
    }


def _atividades_assessor(qs, alvo: User, agora, limit: int = 25) -> list[dict[str, Any]]:
    """Timeline focada no assessor (despachos + conclusões recentes)."""
    itens: list[dict[str, Any]] = []
    att_ids = list(qs.values_list('pk', flat=True)[:5000])

    despachos = (
        Despacho.objects.filter(atendimento_id__in=att_ids, autor_id=alvo.pk)
        .select_related('atendimento', 'responsavel_novo')
        .order_by('-created_at')[:40]
    )
    for d in despachos:
        proto = d.atendimento.protocolo
        if d.tipo == Despacho.Tipo.REATRIBUICAO:
            dest = d.responsavel_novo.nome if d.responsavel_novo else 'outro assessor'
            descricao = f'Transferiu o Atendimento #{proto} para {dest}'
            tipo = 'ticket_transferido'
        elif d.tipo == Despacho.Tipo.MUDANCA_STATUS:
            novo = STATUS_LABEL.get(d.status_novo, d.status_novo or 'atualizado')
            descricao = f'Marcou Atendimento #{proto} como {novo}'
            tipo = 'status_alterado'
        else:
            descricao = f'Registrou andamento no Atendimento #{proto}'
            tipo = 'status_alterado'
        itens.append(
            {
                'id': f'desp-{d.pk}',
                'tipo': tipo,
                'descricao': descricao,
                'timestamp': d.created_at.isoformat(),
            }
        )

    for att in qs.filter(status=Atendimento.Status.CONCLUIDO).order_by('-updated_at')[:15]:
        itens.append(
            {
                'id': f'att-{att.pk}',
                'tipo': 'status_alterado',
                'descricao': f'Concluiu Atendimento #{att.protocolo}',
                'timestamp': att.updated_at.isoformat(),
            }
        )

    itens.sort(key=lambda x: x['timestamp'], reverse=True)
    return itens[:limit]
