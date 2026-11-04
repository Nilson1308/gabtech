"""Exportação CSV — desempenho da equipe e assessor individual."""

from __future__ import annotations

import csv
import re
from io import StringIO

from django.http import HttpResponse
from django.utils import timezone

from atendimentos.models import Atendimento

from .assessor_service import STATUS_UI, _aplicar_periodo, build_assessor_desempenho, build_equipe_desempenho
from .services import _atendimentos_visiveis


def _slug_filename(part: str, max_len: int = 40) -> str:
    safe = re.sub(r'[^\w\-]+', '-', part.strip().lower(), flags=re.UNICODE)
    safe = re.sub(r'-+', '-', safe).strip('-')
    return (safe[:max_len] or 'assessor')


def _csv_response(content: str, filename: str) -> HttpResponse:
    response = HttpResponse(content, content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def build_equipe_desempenho_csv_response(user) -> HttpResponse:
    data = build_equipe_desempenho(user)
    buffer = StringIO()
    buffer.write('\ufeff')
    writer = csv.writer(buffer, delimiter=';')
    writer.writerow(['Relatório — Desempenho da equipe'])
    writer.writerow(['Gerado em', timezone.localtime().strftime('%d/%m/%Y %H:%M')])
    writer.writerow([])
    writer.writerow(
        [
            'Assessor',
            'E-mail',
            'Cargo',
            'Total protocolos',
            'Taxa conclusão (%)',
            'Atrasados (SLA)',
        ],
    )
    for m in data.get('membros', []):
        writer.writerow(
            [
                m['nome'],
                m['email'],
                m.get('cargo', ''),
                m['total_atendimentos'],
                m['taxa_sucesso'],
                m.get('atrasados', ''),
            ],
        )

    hoje = timezone.localdate().isoformat()
    return _csv_response(buffer.getvalue(), f'desempenho-equipe-{hoje}.csv')


def build_assessor_desempenho_csv_response(
    user,
    responsavel_id: int,
    *,
    de=None,
    ate=None,
) -> HttpResponse | None:
    payload = build_assessor_desempenho(user, responsavel_id, de=de, ate=ate)
    if 'detail' in payload and len(payload) == 1:
        return None

    assessor = payload['assessor']
    resumo = payload['resumo']
    comparativo = payload['comparativo_equipe']
    periodo = payload['periodo']

    qs = _aplicar_periodo(
        _atendimentos_visiveis(user).filter(responsavel_id=responsavel_id),
        de,
        ate,
    )

    buffer = StringIO()
    buffer.write('\ufeff')
    writer = csv.writer(buffer, delimiter=';')

    writer.writerow(['Relatório — Desempenho individual'])
    writer.writerow(['Assessor', assessor['nome']])
    writer.writerow(['E-mail', assessor['email']])
    writer.writerow(['Cargo', assessor.get('cargo', '')])
    writer.writerow(['Período de', periodo.get('de') or 'Início'])
    writer.writerow(['Período até', periodo.get('ate') or 'Hoje'])
    writer.writerow(['Gerado em', timezone.localtime().strftime('%d/%m/%Y %H:%M')])
    writer.writerow([])

    writer.writerow(['Resumo'])
    writer.writerow(['Total', resumo['total']])
    writer.writerow(['Concluídos', resumo['concluidos']])
    writer.writerow(['Em andamento', resumo['em_andamento']])
    writer.writerow(['SLA em atraso', resumo['atrasados']])
    writer.writerow(['Taxa de conclusão (%)', resumo['taxa_sucesso']])
    writer.writerow(['Média equipe (%)', comparativo['taxa_sucesso_media']])
    writer.writerow(['Delta vs equipe (pp)', comparativo['delta_taxa']])
    writer.writerow([])

    writer.writerow(['Por status'])
    writer.writerow(['Status', 'Quantidade'])
    for row in payload['por_status']:
        writer.writerow([row['rotulo'], row['quantidade']])
    writer.writerow([])

    writer.writerow(['Por macrotema'])
    writer.writerow(['Macrotema', 'Quantidade'])
    for row in payload['por_macrotema']:
        writer.writerow([row['macrotema'], row['quantidade']])
    writer.writerow([])

    writer.writerow(
        [
            'Protocolo',
            'Assunto',
            'Cidadão',
            'Macrotema',
            'Status',
            'Prioridade',
            'SLA atrasado',
            'Abertura',
            'Última atualização',
        ],
    )
    agora = timezone.now()
    for att in qs.select_related('macrotema', 'cidadao').order_by('-updated_at').iterator():
        atrasado = (
            att.status != Atendimento.Status.CONCLUIDO
            and att.sla_vencimento is not None
            and att.sla_vencimento < agora
        )
        writer.writerow(
            [
                att.protocolo,
                att.assunto,
                att.cidadao.nome if att.cidadao_id else '',
                att.macrotema.nome if att.macrotema_id else '',
                STATUS_UI.get(att.status, att.status),
                att.get_prioridade_display(),
                'Sim' if atrasado else 'Não',
                timezone.localtime(att.created_at).strftime('%d/%m/%Y %H:%M'),
                timezone.localtime(att.updated_at).strftime('%d/%m/%Y %H:%M'),
            ],
        )
    writer.writerow([])

    writer.writerow(['Atividade recente'])
    writer.writerow(['Descrição', 'Data/hora'])
    for ev in payload['atividades']:
        writer.writerow([ev['descricao'], ev['timestamp']])

    slug = _slug_filename(assessor['nome'])
    hoje = timezone.localdate().isoformat()
    return _csv_response(buffer.getvalue(), f'desempenho-{slug}-{hoje}.csv')
