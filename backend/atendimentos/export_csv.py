"""Exportação CSV de atendimentos (relatório)."""

from __future__ import annotations

import csv
from io import StringIO

from django.http import HttpResponse
from django.utils import timezone

from .models import Atendimento


def build_atendimentos_csv_response(queryset) -> HttpResponse:
    buffer = StringIO()
    buffer.write('\ufeff')
    writer = csv.writer(buffer)
    writer.writerow(
        [
            'Protocolo',
            'Assunto',
            'Cidadão',
            'Macrotema',
            'Status',
            'Prioridade',
            'Responsável',
            'Data abertura',
        ],
    )

    for atendimento in queryset.iterator():
        writer.writerow(
            [
                atendimento.protocolo,
                atendimento.assunto,
                atendimento.cidadao.nome if atendimento.cidadao_id else '',
                atendimento.macrotema.nome if atendimento.macrotema_id else '',
                atendimento.get_status_display(),
                atendimento.get_prioridade_display(),
                atendimento.responsavel.nome if atendimento.responsavel_id else '',
                timezone.localtime(atendimento.created_at).strftime('%d/%m/%Y %H:%M'),
            ],
        )

    hoje = timezone.localdate().isoformat()
    response = HttpResponse(buffer.getvalue(), content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="atendimentos-{hoje}.csv"'
    return response


def filtrar_queryset_exportacao(queryset, query_params):
    macrotemas = query_params.getlist('macrotema')
    if macrotemas:
        queryset = queryset.filter(macrotema_id__in=macrotemas)

    tags = query_params.getlist('tag')
    if tags:
        queryset = queryset.filter(tags__in=tags).distinct()

    status = query_params.get('status')
    if status:
        if status in Atendimento.Status.values:
            queryset = queryset.filter(status=status)

    return queryset
