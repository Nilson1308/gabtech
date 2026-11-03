from __future__ import annotations

import html
from dataclasses import dataclass, field
from datetime import datetime, time

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.html import strip_tags
from django.utils import timezone

from atendimentos.models import Atendimento, Despacho, Macrotema
from core.legado.atendimento_edsons79 import (
    AtendimentoLegado,
    carregar_categorias_atendimento,
    extrair_assunto,
    iter_atendimentos,
)
from core.legado.cadastro_edsons79 import (
    CadastroLegado,
    carregar_tags_por_cadastro,
    iter_cadastros,
    ler_sql,
    parse_data,
)
from core.legado.config_edsonsantos import MigracaoConfig
from core.legado.import_fase1_crm import _importar_um, _tag_legado
from crm.models import Cidadao, Endereco, MigracaoLegadoRef, Tag

User = get_user_model()


@dataclass
class ResultadoFase2:
    total_legado: int = 0
    filtrados_stts: int = 0
    ja_importados: int = 0
    criados: int = 0
    cidadaos_vinculados_existentes: int = 0
    cidadaos_importados_sob_demanda: int = 0
    placeholders_cidadao: int = 0
    pulados_sem_cidadao: int = 0
    erros: list[str] = field(default_factory=list)
    dry_run: bool = True

    def resumo(self) -> str:
        modo = 'DRY-RUN' if self.dry_run else 'IMPORTADO'
        return (
            f'[{modo}] atend. legado={self.total_legado} elegíveis={self.filtrados_stts} '
            f'criados={self.criados} já_existiam={self.ja_importados} '
            f'cid_existente={self.cidadaos_vinculados_existentes} '
            f'cid_import_sob_demanda={self.cidadaos_importados_sob_demanda} '
            f'placeholders={self.placeholders_cidadao} pulados={self.pulados_sem_cidadao} '
            f'erros={len(self.erros)}'
        )


def _sanitizar_descricao(raw_html: str, modo: str) -> str:
    texto = html.unescape(raw_html or '')
    if modo == 'sanitizar':
        texto = strip_tags(texto)
    texto = texto.replace('\r\n', '\n').strip()
    return texto[:50000] if texto else '(sem descrição no legado)'


def _datetime_from_date(value: str, *, end_of_day: bool = False) -> datetime | None:
    d = parse_data(value)
    if d is None:
        return None
    t = time.max if end_of_day else time.min
    return timezone.make_aware(datetime.combine(d, t))


def _cache_macrotemas() -> dict[str, Macrotema]:
    return {m.nome: m for m in Macrotema.objects.all()}


def _resolver_macrotema(
    config: MigracaoConfig,
    cache: dict[str, Macrotema],
    v_cat: int,
    v_secr: int | None,
) -> Macrotema:
    nome = config.macrotema_por_categoria.get(v_cat)
    if not nome and v_secr is not None:
        nome = config.macrotema_por_vsecr.get(v_secr)
    if not nome:
        nome = config.macrotema_default
    mac = cache.get(nome)
    if mac:
        return mac
    fallback = cache.get(config.macrotema_default)
    if fallback:
        return fallback
    mac = Macrotema.objects.order_by('pk').first()
    if mac is None:
        raise ValueError('Nenhum macrotema cadastrado no tenant.')
    return mac


def _resolver_responsavel(
    config: MigracaoConfig,
    cache: dict[int, User | None],
    v_usu: int,
) -> User:
    if v_usu in cache:
        user = cache[v_usu]
        if user is None:
            raise ValueError(f'Usuário legado {v_usu} sem mapa válido')
        return user

    email = config.mapa_usuarios_legado.get(str(v_usu))
    if email:
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            raise ValueError(f'E-mail não encontrado no tenant: {email} (legado vUsu={v_usu})')
        cache[v_usu] = user
        return user

    default_email = config.default_responsavel_email
    user = User.objects.filter(email__iexact=default_email).first()
    if not user:
        raise ValueError(f'Responsável padrão não encontrado: {default_email}')
    cache[v_usu] = user
    return user


def _tag_canal(tipo: str) -> Tag | None:
    t = (tipo or '').strip()
    if not t:
        return None
    nome = f'Canal: {t[:100]}'
    return _tag_legado(nome)


@transaction.atomic
def _criar_placeholder_cidadao(config: MigracaoConfig, v_cad: int) -> Cidadao:
    nome = f'{config.placeholder_nome} (#{v_cad})'[:200]
    cidadao = Cidadao.objects.create(
        nome=nome,
        telefone='(legado)',
        observacoes=f'[legado:cad:{v_cad}] Cidadão ausente no CRM — criado na migração de atendimentos.',
    )
    Endereco.objects.create(cidadao=cidadao, logradouro='', numero='', bairro='', cidade='', estado='SP', cep='')
    MigracaoLegadoRef.objects.create(
        tipo=MigracaoLegadoRef.Tipo.CADASTRO,
        legacy_id=v_cad,
        gabtech_id=cidadao.pk,
        meta={'placeholder': True},
    )
    return cidadao


def _resolver_cidadao(
    config: MigracaoConfig,
    v_cad: int,
    cadastros: dict[int, CadastroLegado],
    tags_map: dict[int, list[str]],
    cpf_vistos: set[str],
    stats: ResultadoFase2,
) -> Cidadao | None:
    ref = MigracaoLegadoRef.objects.filter(
        tipo=MigracaoLegadoRef.Tipo.CADASTRO,
        legacy_id=v_cad,
    ).first()
    if ref:
        return Cidadao.objects.get(pk=ref.gabtech_id)

    row = cadastros.get(v_cad)
    if row is not None:
        try:
            _importar_um(row, tags_map.get(v_cad, []), cpf_vistos, config.deduplicar_cpf)
            stats.cidadaos_importados_sob_demanda += 1
            ref = MigracaoLegadoRef.objects.get(tipo=MigracaoLegadoRef.Tipo.CADASTRO, legacy_id=v_cad)
            return Cidadao.objects.get(pk=ref.gabtech_id)
        except Exception as exc:
            stats.erros.append(f'cad sob demanda {v_cad}: {exc} — usando placeholder')

    if config.orfaos_vcad == 'pular':
        return None
    if config.orfaos_vcad == 'criar_cidadao_placeholder':
        cidadao = _criar_placeholder_cidadao(config, v_cad)
        stats.placeholders_cidadao += 1
        return cidadao

    return None


@transaction.atomic
def _importar_atendimento(
    row: AtendimentoLegado,
    *,
    config: MigracaoConfig,
    categorias: dict,
    macrotema_cache: dict[str, Macrotema],
    responsavel: User,
    cidadao: Cidadao,
    status: str,
    assunto: str,
    descricao: str,
) -> int:
    cat = categorias.get(row.v_cat)
    macrotema = _resolver_macrotema(
        config,
        macrotema_cache,
        row.v_cat,
        cat.v_secr if cat else None,
    )

    atendimento = Atendimento(
        cidadao=cidadao,
        assunto=assunto,
        descricao=descricao,
        macrotema=macrotema,
        status=status,
        responsavel=responsavel,
        prioridade=Atendimento.Prioridade.MEDIA,
    )
    if status == Atendimento.Status.CONCLUIDO:
        atendimento.sla_vencimento = None
    atendimento.save()

    created = _datetime_from_date(row.dt_ini) or timezone.now()
    updated = _datetime_from_date(row.dt_enc, end_of_day=True) or created
    Atendimento.objects.filter(pk=atendimento.pk).update(created_at=created, updated_at=updated)

    if config.canal_como_tag and row.tipo:
        tag = _tag_canal(row.tipo)
        if tag:
            atendimento.tags.set([tag])

    Despacho.objects.create(
        atendimento=atendimento,
        autor=responsavel,
        tipo=Despacho.Tipo.NOTA_PUBLICA,
        conteudo=f'Importado do sistema legado (atendimento ID {row.legacy_id}).',
    )

    MigracaoLegadoRef.objects.create(
        tipo=MigracaoLegadoRef.Tipo.ATENDIMENTO,
        legacy_id=row.legacy_id,
        gabtech_id=atendimento.pk,
        meta={
            'v_cad': row.v_cad,
            'v_cat': row.v_cat,
            'v_usu': row.v_usu,
            'stts': row.stts,
            'tipo': row.tipo,
        },
    )
    return atendimento.pk


def executar_fase2_atendimentos(
    config: MigracaoConfig,
    *,
    dry_run: bool = True,
    limit: int | None = None,
) -> ResultadoFase2:
    res = ResultadoFase2(dry_run=dry_run)
    sql_text = ler_sql(config.sql_path)
    atendimentos = iter_atendimentos(sql_text)
    categorias = carregar_categorias_atendimento(sql_text)
    cadastros = {c.legacy_id: c for c in iter_cadastros(sql_text)}
    tags_map = carregar_tags_por_cadastro(sql_text)

    res.total_legado = len(atendimentos)
    permitidos = config.importar_stts_atendimento
    elegiveis = [a for a in atendimentos if a.stts in permitidos]
    if limit is not None:
        elegiveis = elegiveis[:limit]
    res.filtrados_stts = len(elegiveis)

    existentes = set(
        MigracaoLegadoRef.objects.filter(tipo=MigracaoLegadoRef.Tipo.ATENDIMENTO).values_list(
            'legacy_id',
            flat=True,
        ),
    )

    macrotema_cache = _cache_macrotemas()
    responsavel_cache: dict[int, User | None] = {}
    cpf_vistos: set[str] = set(
        Cidadao.objects.exclude(cpf__isnull=True).exclude(cpf='').values_list('cpf', flat=True),
    )

    for row in elegiveis:
        if row.legacy_id in existentes:
            res.ja_importados += 1
            continue

        status = config.mapear_stts_atendimento.get(row.stts)
        if not status:
            res.erros.append(f'at {row.legacy_id}: stts {row.stts} sem mapeamento')
            continue

        assunto = extrair_assunto(categorias, row.v_cat)
        descricao = _sanitizar_descricao(row.descr, config.html_descricao)

        if dry_run:
            ref_cad = MigracaoLegadoRef.objects.filter(
                tipo=MigracaoLegadoRef.Tipo.CADASTRO,
                legacy_id=row.v_cad,
            ).exists()
            if ref_cad:
                res.cidadaos_vinculados_existentes += 1
            elif row.v_cad in cadastros:
                res.cidadaos_importados_sob_demanda += 1
            elif config.orfaos_vcad == 'criar_cidadao_placeholder':
                res.placeholders_cidadao += 1
            elif config.orfaos_vcad == 'pular':
                res.pulados_sem_cidadao += 1
                continue
            try:
                _resolver_responsavel(config, responsavel_cache, row.v_usu)
            except ValueError as exc:
                res.erros.append(f'at {row.legacy_id}: {exc}')
                continue
            res.criados += 1
            continue

        try:
            with transaction.atomic():
                cidadao = _resolver_cidadao(config, row.v_cad, cadastros, tags_map, cpf_vistos, res)
                if cidadao is None:
                    res.pulados_sem_cidadao += 1
                    continue
                responsavel = _resolver_responsavel(config, responsavel_cache, row.v_usu)
                _importar_atendimento(
                    row,
                    config=config,
                    categorias=categorias,
                    macrotema_cache=macrotema_cache,
                    responsavel=responsavel,
                    cidadao=cidadao,
                    status=status,
                    assunto=assunto,
                    descricao=descricao,
                )
            res.criados += 1
        except Exception as exc:
            res.erros.append(f'at {row.legacy_id}: {exc}')

    return res
