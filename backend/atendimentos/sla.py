"""Cálculo de SLA — prazos lidos de ConfiguracaoSla (tenant)."""

from __future__ import annotations

from datetime import datetime, timedelta

from django.utils import timezone

DEFAULT_SLA_HORAS = 72
HORAS_POR_DIA_SLA = 24


def horas_sla_para_prioridade(prioridade: str) -> int:
    from .models import ConfiguracaoSla

    return ConfiguracaoSla.get().horas_para_prioridade(prioridade)


def calcular_sla_vencimento(
    prioridade: str,
    *,
    base: datetime | None = None,
) -> datetime:
    inicio = base or timezone.now()
    horas = horas_sla_para_prioridade(prioridade)
    return inicio + timedelta(hours=horas)
