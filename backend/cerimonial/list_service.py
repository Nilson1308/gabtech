"""Agregações leves para listagem de eventos (sem carregar todos os registros)."""

from __future__ import annotations

from django.db.models import Count

from agenda.models import Evento

from .models import EventoCerimonial


def build_eventos_resumo() -> dict:
    por_status_raw = {
        row['status_logistico']: row['c']
        for row in EventoCerimonial.objects.values('status_logistico').annotate(c=Count('id'))
    }
    confirmados = EventoCerimonial.objects.filter(
        evento_agenda__status=Evento.Status.AGENDADO,
        status_logistico=EventoCerimonial.StatusLogistico.PLANEJAMENTO,
    ).count()

    return {
        'total': EventoCerimonial.objects.count(),
        'confirmados': confirmados,
        'por_status': {
            'planejamento': por_status_raw.get(EventoCerimonial.StatusLogistico.PLANEJAMENTO, 0),
            'executando': por_status_raw.get(EventoCerimonial.StatusLogistico.EXECUTANDO, 0),
            'concluido': por_status_raw.get(EventoCerimonial.StatusLogistico.CONCLUIDO, 0),
            'cancelado': por_status_raw.get(EventoCerimonial.StatusLogistico.CANCELADO, 0),
        },
    }
