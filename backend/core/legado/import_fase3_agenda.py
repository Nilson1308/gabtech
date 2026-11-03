from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from agenda.models import Evento, TipoEvento
from core.legado.agenda_edsons79 import EventoLegado, iter_eventos, montar_descricao_evento, nome_tipo_evento
from core.legado.cadastro_edsons79 import ler_sql
from core.legado.config_edsonsantos import MigracaoConfig
from crm.models import MigracaoLegadoRef

User = get_user_model()


@dataclass
class ResultadoFase3:
    total_legado: int = 0
    ja_importados: int = 0
    criados: int = 0
    tipos_criados: int = 0
    erros: list[str] = field(default_factory=list)
    dry_run: bool = True

    def resumo(self) -> str:
        modo = 'DRY-RUN' if self.dry_run else 'IMPORTADO'
        return (
            f'[{modo}] eventos legado={self.total_legado} criados={self.criados} '
            f'já_existiam={self.ja_importados} tipos_novos={self.tipos_criados} erros={len(self.erros)}'
        )


def _parse_datetime(value: str) -> datetime | None:
    value = (value or '').strip()
    if not value or value.startswith('0000'):
        return None
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'):
        try:
            dt = datetime.strptime(value[:19], fmt)
            return timezone.make_aware(dt)
        except ValueError:
            continue
    return None


def _resolver_status(row: EventoLegado, config: MigracaoConfig, fim: datetime | None) -> str:
    tag_nome = nome_tipo_evento(row)
    tag_cfg = config.agenda_tipo_evento_por_tag.get(tag_nome) or {}
    if tag_cfg.get('status') == Evento.Status.CANCELADO:
        return Evento.Status.CANCELADO
    if config.agenda_status_por_stts.get(row.stts) == Evento.Status.CANCELADO:
        return Evento.Status.CANCELADO
    if config.agenda_status_por_stts.get(row.tag) == Evento.Status.CANCELADO:
        return Evento.Status.CANCELADO
    if tag_nome.lower() == 'cancelado':
        return Evento.Status.CANCELADO
    if fim and fim < timezone.now():
        return Evento.Status.REALIZADO
    return Evento.Status.AGENDADO


def _get_or_create_tipo(
    nome: str,
    config: MigracaoConfig,
    cache: dict[str, TipoEvento],
    stats: ResultadoFase3,
) -> TipoEvento:
    if nome in cache:
        return cache[nome]
    cfg = config.agenda_tipo_evento_por_tag.get(nome, {})
    defaults = {
        'cor': str(cfg.get('cor', '#3b82f6'))[:7],
        'icone': str(cfg.get('icone', 'calendar'))[:50],
        'ativo': True,
    }
    tipo, created = TipoEvento.objects.get_or_create(nome=nome[:120], defaults=defaults)
    if created:
        stats.tipos_criados += 1
    cache[nome] = tipo
    return tipo


def _resolver_criador(config: MigracaoConfig) -> User | None:
    email = config.default_responsavel_email
    return User.objects.filter(email__iexact=email).first()


@transaction.atomic
def _importar_evento(
    row: EventoLegado,
    *,
    config: MigracaoConfig,
    tipo: TipoEvento,
    criador: User | None,
    inicio: datetime,
    fim: datetime,
    status: str,
) -> int:
    evento = Evento.objects.create(
        titulo=row.titulo[:255] or f'Evento legado #{row.legacy_id}',
        descricao=montar_descricao_evento(row),
        data=inicio.date(),
        hora_inicio=inicio.time(),
        hora_fim=fim.time(),
        tipo=tipo,
        status=status,
        criado_por=criador,
    )
    Evento.objects.filter(pk=evento.pk).update(created_at=inicio, updated_at=fim)

    MigracaoLegadoRef.objects.create(
        tipo=MigracaoLegadoRef.Tipo.EVENTO,
        legacy_id=row.legacy_id,
        gabtech_id=evento.pk,
        meta={'tag': row.tag, 'stts': row.stts},
    )
    return evento.pk


def executar_fase3_agenda(
    config: MigracaoConfig,
    *,
    dry_run: bool = True,
    limit: int | None = None,
) -> ResultadoFase3:
    res = ResultadoFase3(dry_run=dry_run)
    if not config.agenda_importar:
        res.erros.append('agenda.importar=false no YAML — nada a fazer.')
        return res

    sql_text = ler_sql(config.sql_path)
    eventos = iter_eventos(sql_text)
    if limit is not None:
        eventos = eventos[:limit]
    res.total_legado = len(eventos)

    existentes = set(
        MigracaoLegadoRef.objects.filter(tipo=MigracaoLegadoRef.Tipo.EVENTO).values_list(
            'legacy_id',
            flat=True,
        ),
    )

    tipo_cache: dict[str, TipoEvento] = {t.nome: t for t in TipoEvento.objects.all()}
    tipos_vistos_dry: set[str] = set(tipo_cache.keys())
    criador = _resolver_criador(config)

    for row in eventos:
        if row.legacy_id in existentes:
            res.ja_importados += 1
            continue

        inicio = _parse_datetime(row.inicio)
        fim = _parse_datetime(row.termino)
        if inicio is None:
            res.erros.append(f'ev {row.legacy_id}: data início inválida ({row.inicio!r})')
            continue
        if fim is None or fim < inicio:
            fim = inicio

        tag_nome = nome_tipo_evento(row)
        status = _resolver_status(row, config, fim)

        if dry_run:
            if tag_nome not in tipos_vistos_dry:
                tipos_vistos_dry.add(tag_nome)
                res.tipos_criados += 1
            res.criados += 1
            continue

        try:
            with transaction.atomic():
                tipo = _get_or_create_tipo(tag_nome, config, tipo_cache, res)
                _importar_evento(
                    row,
                    config=config,
                    tipo=tipo,
                    criador=criador,
                    inicio=inicio,
                    fim=fim,
                    status=status,
                )
            res.criados += 1
        except Exception as exc:
            res.erros.append(f'ev {row.legacy_id}: {exc}')

    return res
