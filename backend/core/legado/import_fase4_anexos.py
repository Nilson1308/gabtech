from __future__ import annotations

import mimetypes
import os
from dataclasses import dataclass, field
from datetime import datetime, time
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files import File
from django.db import transaction
from django.utils import timezone

from atendimentos.models import Anexo, Atendimento
from core.legado.anexos_edsons79 import (
    AtendimentoDocLegado,
    CadastroDocLegado,
    iter_atendimento_docs,
    iter_cadastro_docs,
)
from core.legado.cadastro_edsons79 import ler_sql, parse_data
from core.legado.config_edsonsantos import MigracaoConfig
from crm.models import Cidadao, DocumentoAnexo, MigracaoLegadoRef

User = get_user_model()


@dataclass
class ResultadoFase4:
    cadastro_meta: int = 0
    cadastro_com_arquivo: int = 0
    atendimento_meta: int = 0
    atendimento_com_arquivo: int = 0
    ja_importados_cadastro: int = 0
    ja_importados_atendimento: int = 0
    criados_cadastro: int = 0
    criados_atendimento: int = 0
    arquivo_ausente_disco: int = 0
    sem_ref_cidadao: int = 0
    sem_ref_atendimento: int = 0
    pulados_sem_arquivo_meta: int = 0
    erros: list[str] = field(default_factory=list)
    dry_run: bool = True

    def resumo(self) -> str:
        modo = 'DRY-RUN' if self.dry_run else 'IMPORTADO'
        return (
            f'[{modo}] cad_docs meta={self.cadastro_meta} com_arquivo={self.cadastro_com_arquivo} '
            f'criados={self.criados_cadastro} | atend_docs meta={self.atendimento_meta} '
            f'com_arquivo={self.atendimento_com_arquivo} criados={self.criados_atendimento} | '
            f'já_existiam cad={self.ja_importados_cadastro} at={self.ja_importados_atendimento} | '
            f'arquivo_ausente={self.arquivo_ausente_disco} sem_ref_cid={self.sem_ref_cidadao} '
            f'sem_ref_at={self.sem_ref_atendimento} pulados_sem_meta={self.pulados_sem_arquivo_meta} '
            f'erros={len(self.erros)}'
        )


def _nome_exibicao(arquivo: str, descr: str, legacy_id: int) -> str:
    nome = (arquivo or '').strip()
    if not nome:
        nome = (descr or f'legado-{legacy_id}').strip()
    if nome.endswith('.'):
        nome = f'{nome}bin'
    return nome[:255]


def _extensao_de_arquivo(nome: str) -> str:
    ext = os.path.splitext(nome)[1].lower()
    if ext:
        return ext
    return ''


def _content_type(nome: str) -> str:
    guessed, _ = mimetypes.guess_type(nome)
    return guessed or 'application/octet-stream'


def _datetime_from_date(value: str) -> datetime | None:
    d = parse_data(value)
    if d is None:
        return None
    return timezone.make_aware(datetime.combine(d, time.min))


def localizar_arquivo_legacy(root: Path | None, nome: str, subpastas: list[str]) -> Path | None:
    if root is None or not nome.strip():
        return None
    nome = nome.strip()
    candidatos: list[Path] = [root / nome]
    for sub in subpastas:
        if sub:
            candidatos.append(root / sub / nome)
    if nome.endswith('.'):
        for ext in ('pdf', 'jpeg', 'jpg', 'png', 'doc', 'docx'):
            candidatos.append(root / f'{nome}{ext}')
            for sub in subpastas:
                if sub:
                    candidatos.append(root / sub / f'{nome}{ext}')
    for path in candidatos:
        if path.is_file():
            return path
    # Busca por basename (uploads PHP em subpastas)
    try:
        hits = [p for p in root.rglob(nome) if p.is_file()]
        if len(hits) == 1:
            return hits[0]
        if nome.endswith('.'):
            prefix = nome
            ext_hits = [p for p in root.rglob(f'{prefix}*') if p.is_file() and p.name.startswith(prefix)]
            if len(ext_hits) == 1:
                return ext_hits[0]
    except OSError:
        return None
    return None


def _map_categoria_cadastro(config: MigracaoConfig, tipo: str) -> str:
    mapa = config.anexos_mapa_tipo_cadastro
    key = (tipo or '').strip()
    for candidato in (key, key.lower(), key.title()):
        if candidato in mapa:
            return mapa[candidato]
    if 'curric' in key.lower():
        return DocumentoAnexo.Categoria.CURRICULO
    return DocumentoAnexo.Categoria.OUTROS


def _resolver_gabtech_id(tipo_ref: str, legacy_id: int) -> int | None:
    ref = MigracaoLegadoRef.objects.filter(tipo=tipo_ref, legacy_id=legacy_id).first()
    return ref.gabtech_id if ref else None


@transaction.atomic
def _importar_doc_cidadao(
    row: CadastroDocLegado,
    *,
    src: Path,
    cidadao: Cidadao,
    categoria: str,
    enviado_por: User | None,
    nome_original: str,
) -> int:
    tamanho = src.stat().st_size
    doc = DocumentoAnexo(
        cidadao=cidadao,
        categoria=categoria,
        nome_original=nome_original,
        content_type=_content_type(nome_original),
        tamanho=tamanho,
        enviado_por=enviado_por,
    )
    with src.open('rb') as handle:
        doc.arquivo.save(os.path.basename(nome_original), File(handle), save=False)
    doc.save()
    created = _datetime_from_date(row.data)
    if created:
        DocumentoAnexo.objects.filter(pk=doc.pk).update(created_at=created)
    MigracaoLegadoRef.objects.create(
        tipo=MigracaoLegadoRef.Tipo.ANEXO_CADASTRO,
        legacy_id=row.legacy_id,
        gabtech_id=doc.pk,
        meta={'v_cad': row.v_cad, 'tipo': row.tipo, 'descr': row.descr, 'arquivo': row.arquivo},
    )
    return doc.pk


@transaction.atomic
def _importar_anexo_atendimento(
    row: AtendimentoDocLegado,
    *,
    src: Path,
    atendimento: Atendimento,
    enviado_por: User | None,
    nome_original: str,
) -> int:
    tamanho = src.stat().st_size
    anexo = Anexo(
        atendimento=atendimento,
        nome_original=nome_original,
        content_type=_content_type(nome_original),
        tamanho=tamanho,
        enviado_por=enviado_por,
    )
    with src.open('rb') as handle:
        anexo.arquivo.save(os.path.basename(nome_original), File(handle), save=False)
    anexo.save()
    created = _datetime_from_date(row.data)
    if created:
        Anexo.objects.filter(pk=anexo.pk).update(created_at=created)
    MigracaoLegadoRef.objects.create(
        tipo=MigracaoLegadoRef.Tipo.ANEXO_ATENDIMENTO,
        legacy_id=row.legacy_id,
        gabtech_id=anexo.pk,
        meta={'v_atend': row.v_atend, 'tipo': row.tipo, 'descr': row.descr, 'arquivo': row.arquivo},
    )
    return anexo.pk


def executar_fase4_anexos(
    config: MigracaoConfig,
    *,
    dry_run: bool = True,
    limit: int | None = None,
) -> ResultadoFase4:
    res = ResultadoFase4(dry_run=dry_run)
    if not config.anexos_importar:
        res.erros.append('anexos.importar=false no YAML.')
        return res

    sql_text = ler_sql(config.sql_path)
    cad_docs = iter_cadastro_docs(sql_text)
    at_docs = iter_atendimento_docs(sql_text)
    if limit is not None:
        cad_docs = cad_docs[:limit]
        at_docs = at_docs[:limit]

    res.cadastro_meta = len(cad_docs)
    res.atendimento_meta = len(at_docs)
    res.cadastro_com_arquivo = sum(1 for r in cad_docs if r.arquivo.strip())
    res.atendimento_com_arquivo = sum(1 for r in at_docs if r.arquivo.strip())

    existentes_cad = set(
        MigracaoLegadoRef.objects.filter(tipo=MigracaoLegadoRef.Tipo.ANEXO_CADASTRO).values_list(
            'legacy_id',
            flat=True,
        ),
    )
    existentes_at = set(
        MigracaoLegadoRef.objects.filter(tipo=MigracaoLegadoRef.Tipo.ANEXO_ATENDIMENTO).values_list(
            'legacy_id',
            flat=True,
        ),
    )

    enviado_por = User.objects.filter(email__iexact=config.default_responsavel_email).first()
    root = config.media_legacy_root
    subpastas = config.anexos_subpastas_busca

    if not dry_run and root is None:
        res.erros.append(
            'Defina fonte.media_legacy_root no YAML (pasta de uploads do PHP) antes de --executar.',
        )
        return res

    for row in cad_docs:
        if row.legacy_id in existentes_cad:
            res.ja_importados_cadastro += 1
            continue
        if not row.arquivo.strip():
            res.pulados_sem_arquivo_meta += 1
            continue

        gab_cid = _resolver_gabtech_id(MigracaoLegadoRef.Tipo.CADASTRO, row.v_cad)
        if gab_cid is None:
            res.sem_ref_cidadao += 1
            continue

        src = localizar_arquivo_legacy(root, row.arquivo, subpastas) if root else None
        if root is not None and src is None:
            res.arquivo_ausente_disco += 1
            if not dry_run and config.anexos_se_arquivo_ausente != 'registrar_log':
                res.erros.append(f'cad_doc {row.legacy_id}: arquivo não encontrado: {row.arquivo}')
            continue

        if dry_run:
            res.criados_cadastro += 1
            continue

        if src is None:
            res.arquivo_ausente_disco += 1
            continue

        try:
            cidadao = Cidadao.objects.get(pk=gab_cid)
            with transaction.atomic():
                _importar_doc_cidadao(
                    row,
                    src=src,
                    cidadao=cidadao,
                    categoria=_map_categoria_cadastro(config, row.tipo),
                    enviado_por=enviado_por,
                    nome_original=_nome_exibicao(row.arquivo, row.descr, row.legacy_id),
                )
            res.criados_cadastro += 1
        except Exception as exc:
            res.erros.append(f'cad_doc {row.legacy_id}: {exc}')

    for row in at_docs:
        if row.legacy_id in existentes_at:
            res.ja_importados_atendimento += 1
            continue
        if not row.arquivo.strip():
            res.pulados_sem_arquivo_meta += 1
            continue

        gab_at = _resolver_gabtech_id(MigracaoLegadoRef.Tipo.ATENDIMENTO, row.v_atend)
        if gab_at is None:
            res.sem_ref_atendimento += 1
            continue

        src = localizar_arquivo_legacy(root, row.arquivo, subpastas) if root else None
        if root is not None and src is None:
            res.arquivo_ausente_disco += 1
            continue

        if dry_run:
            res.criados_atendimento += 1
            continue

        if src is None:
            res.arquivo_ausente_disco += 1
            continue

        try:
            atendimento = Atendimento.objects.get(pk=gab_at)
            with transaction.atomic():
                _importar_anexo_atendimento(
                    row,
                    src=src,
                    atendimento=atendimento,
                    enviado_por=enviado_por,
                    nome_original=_nome_exibicao(row.arquivo, row.descr, row.legacy_id),
                )
            res.criados_atendimento += 1
        except Exception as exc:
            res.erros.append(f'at_doc {row.legacy_id}: {exc}')

    return res
