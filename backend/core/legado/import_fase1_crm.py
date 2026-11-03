from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time

from django.db import transaction
from django.utils import timezone

from core.legado.cadastro_edsons79 import (
    CadastroLegado,
    carregar_tags_por_cadastro,
    escolher_telefone,
    iter_cadastros,
    ler_sql,
    montar_observacoes,
    normalizar_cpf,
    parse_data,
)
from core.legado.config_edsonsantos import MigracaoConfig
from crm.models import Cidadao, Endereco, MigracaoLegadoRef, Tag


@dataclass
class ResultadoFase1:
    total_legado: int = 0
    filtrados_stts: int = 0
    ja_importados: int = 0
    cpf_duplicado_pulados: int = 0
    criados: int = 0
    erros: list[str] = field(default_factory=list)
    dry_run: bool = True

    def resumo(self) -> str:
        modo = 'DRY-RUN' if self.dry_run else 'IMPORTADO'
        return (
            f'[{modo}] legado={self.total_legado} elegíveis={self.filtrados_stts} '
            f'criados={self.criados} já_existiam={self.ja_importados} '
            f'cpf_dup_pulados={self.cpf_duplicado_pulados} erros={len(self.erros)}'
        )


def _tag_legado(nome: str) -> Tag:
    tag, _ = Tag.objects.get_or_create(
        nome=nome[:120],
        defaults={
            'cor': '#6b7280',
            'tipo': Tag.Tipo.SEGMENTACAO,
            'modulos': ['crm', 'atendimentos'],
        },
    )
    return tag


def _created_at_from(row: CadastroLegado) -> datetime:
    d = parse_data(row.data_cad)
    if d is None:
        return timezone.now()
    return timezone.make_aware(datetime.combine(d, time.min))


@transaction.atomic
def _importar_um(
    row: CadastroLegado,
    tags_vcad: list[str],
    cpf_vistos: set[str],
    deduplicar_cpf: bool,
) -> int:
    cpf_norm = normalizar_cpf(row.cpf)
    if deduplicar_cpf and cpf_norm:
        if cpf_norm in cpf_vistos:
            raise ValueError(f'CPF duplicado no lote: {cpf_norm}')
        if Cidadao.objects.filter(cpf=cpf_norm).exists():
            raise ValueError(f'CPF já existe no tenant: {cpf_norm}')
        cpf_vistos.add(cpf_norm)

    cidadao = Cidadao(
        nome=row.nome[:200] or f'Sem nome (legado {row.legacy_id})',
        nome_social=row.apelido[:200],
        cpf=cpf_norm,
        telefone=escolher_telefone(row.celular, row.telefone),
        email=row.email[:254] if row.email else '',
        observacoes=montar_observacoes(row),
    )
    cidadao.save()
    created = _created_at_from(row)
    Cidadao.objects.filter(pk=cidadao.pk).update(created_at=created, updated_at=created)

    Endereco.objects.create(
        cidadao=cidadao,
        logradouro=row.logradouro[:200],
        numero=str(row.num)[:20],
        complemento=row.compl[:100],
        bairro=row.bairro[:120],
        cidade=row.cidade[:120],
        estado=(row.uf or 'SP')[:2].upper(),
        cep=row.cep[:9],
    )

    marcadores = [_tag_legado(t) for t in tags_vcad if t.strip()]
    if marcadores:
        cidadao.marcadores.set(marcadores)

    MigracaoLegadoRef.objects.create(
        tipo=MigracaoLegadoRef.Tipo.CADASTRO,
        legacy_id=row.legacy_id,
        gabtech_id=cidadao.pk,
        meta={'stts': row.stts, 'v_usu': row.v_usu},
    )
    return cidadao.pk


def executar_fase1_crm(
    config: MigracaoConfig,
    *,
    dry_run: bool = True,
    limit: int | None = None,
) -> ResultadoFase1:
    res = ResultadoFase1(dry_run=dry_run)
    sql_text = ler_sql(config.sql_path)
    cadastros = iter_cadastros(sql_text)
    tags_map = carregar_tags_por_cadastro(sql_text)
    res.total_legado = len(cadastros)

    permitidos = config.importar_stts_cadastro
    elegiveis = [c for c in cadastros if c.stts in permitidos]
    if limit is not None:
        elegiveis = elegiveis[:limit]
    res.filtrados_stts = len(elegiveis)

    existentes = set(
        MigracaoLegadoRef.objects.filter(tipo=MigracaoLegadoRef.Tipo.CADASTRO).values_list(
            'legacy_id',
            flat=True,
        ),
    )
    cpf_vistos: set[str] = set()

    for row in elegiveis:
        if row.legacy_id in existentes:
            res.ja_importados += 1
            continue
        if dry_run:
            cpf_norm = normalizar_cpf(row.cpf)
            if config.deduplicar_cpf and cpf_norm and cpf_norm in cpf_vistos:
                res.cpf_duplicado_pulados += 1
                continue
            if config.deduplicar_cpf and cpf_norm and Cidadao.objects.filter(cpf=cpf_norm).exists():
                res.cpf_duplicado_pulados += 1
                continue
            if cpf_norm:
                cpf_vistos.add(cpf_norm)
            res.criados += 1
            continue
        try:
            with transaction.atomic():
                _importar_um(
                    row,
                    tags_map.get(row.legacy_id, []),
                    cpf_vistos,
                    config.deduplicar_cpf,
                )
            res.criados += 1
        except ValueError as exc:
            if 'CPF' in str(exc):
                res.cpf_duplicado_pulados += 1
            else:
                res.erros.append(f'cad {row.legacy_id}: {exc}')
        except Exception as exc:
            res.erros.append(f'cad {row.legacy_id}: {exc}')

    return res
