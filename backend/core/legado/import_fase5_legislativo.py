from __future__ import annotations

import csv
import html
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.files.storage import default_storage
from django.db import transaction
from django.utils import timezone

from core.legado.config_edsonsantos import MigracaoConfig
from core.legado.import_fase4_anexos import localizar_arquivo_legacy
from core.legado.legislativo_edsons79 import LegislativoLegado, iter_legislativo
from core.legado.cadastro_edsons79 import ler_sql
from crm.models import MigracaoLegadoRef
from documentos.models import Documento, EtiquetaDocumento, PastaDocumento, TipoDocumento

User = get_user_model()

TIPO_REF = MigracaoLegadoRef.Tipo.LEGISLATIVO


@dataclass
class ResultadoFase5:
    total_legado: int = 0
    criados: int = 0
    ja_importados: int = 0
    pulados_modo: int = 0
    arquivos_copiados: int = 0
    arquivos_ausentes: int = 0
    links_http: int = 0
    sem_link: int = 0
    csv_path: str | None = None
    erros: list[str] = field(default_factory=list)
    dry_run: bool = True

    def resumo(self) -> str:
        modo = 'DRY-RUN' if self.dry_run else 'IMPORTADO'
        extra = f' csv={self.csv_path}' if self.csv_path else ''
        return (
            f'[{modo}] legislativo total={self.total_legado} criados={self.criados} '
            f'já_existiam={self.ja_importados} arquivos_ok={self.arquivos_copiados} '
            f'arquivos_ausente={self.arquivos_ausentes} http={self.links_http} sem_link={self.sem_link}'
            f'{extra} erros={len(self.erros)}'
        )


def _cfg_legislativo(config: MigracaoConfig) -> dict[str, Any]:
    raw = config.raw.get('legislativo', {})
    return raw if isinstance(raw, dict) else {}


def _mapa_natureza(config: MigracaoConfig) -> dict[str, str]:
    defaults = {
        'Projeto de Lei Ordinária': 'projeto_lei',
        'Projeto de Lei Complementar': 'projeto_lei',
        'Projeto de Decreto Legislativo': 'projeto_lei',
        'Requerimento': 'requerimento',
        'Indicação': 'indicacao',
        'Moção': 'mocao',
        'Ofício': 'oficio',
        'Parecer': 'parecer',
        'Relatório': 'relatorio',
        'Ata': 'ata',
        'Declaração': 'declaracao',
    }
    raw = _cfg_legislativo(config).get('mapa_natureza_tipo', {})
    merged = {**defaults, **{str(k): str(v) for k, v in raw.items()}}
    return merged


def _status_documento(stts_legado: str) -> str:
    s = (stts_legado or '').strip().lower()
    if not s:
        return Documento.Status.RASCUNHO
    if any(x in s for x in ('aprovado', 'lei n', 'decreto', 'protocolado', 'cancelado', 'retirado')):
        return Documento.Status.FINALIZADO
    return Documento.Status.RASCUNHO


def _titulo(row: LegislativoLegado) -> str:
    num = row.num or '—'
    ano = row.ano or '—'
    assunto = re.sub(r'\s+', ' ', row.assunto).strip()
    if len(assunto) > 380:
        assunto = f'{assunto[:377]}…'
    return f'{num}/{ano} — {assunto}'


def _campo(label: str, valor: str) -> str:
    v = (valor or '').strip()
    if not v:
        return ''
    return f'<dt>{html.escape(label)}</dt><dd>{html.escape(v)}</dd>'


def _montar_conteudo_html(
    row: LegislativoLegado,
    *,
    link_anexo: str | None,
    link_rotulo: str,
) -> str:
    partes = [
        '<p><em>Importado do acervo legado (CMMC / tbLegislativo).</em></p>',
        '<dl>',
        _campo('Número', row.num),
        _campo('Ano', row.ano),
        _campo('Natureza', row.natureza),
        _campo('Processo / tramitação', row.processo),
        _campo('Situação (legado)', row.stts),
        _campo('Solicitante', row.solic),
        _campo('Destinatário', row.dest),
        _campo('Observações', row.obs),
        '</dl>',
    ]
    if link_anexo:
        partes.append(
            f'<p><a href="{html.escape(link_anexo)}" target="_blank" rel="noopener noreferrer">'
            f'{html.escape(link_rotulo)}</a></p>',
        )
    elif row.link.strip():
        partes.append(f'<p>Referência legado: {html.escape(row.link.strip())}</p>')
    return '\n'.join(partes)


def _resolver_link(
    row: LegislativoLegado,
    config: MigracaoConfig,
    *,
    dry_run: bool,
) -> tuple[str | None, str, bool, bool]:
    """
    Retorna (url_publica, rótulo, copiou_arquivo, arquivo_ausente).
    """
    link = (row.link or '').strip()
    if not link:
        return None, '', False, False

    if link.startswith('http://') or link.startswith('https://'):
        return link, 'Abrir texto na CMMC (link externo)', False, False

    leg_cfg = _cfg_legislativo(config)
    if not leg_cfg.get('copiar_arquivos_locais', True):
        return None, link, False, True

    root = config.media_legacy_root
    subpastas = config.anexos_subpastas_busca
    src = localizar_arquivo_legacy(root, link, subpastas) if root else None
    if src is None:
        return None, link, False, True

    subpath = str(leg_cfg.get('media_subpath', 'documentos_legado')).strip('/')
    basename = os.path.basename(link)
    if basename.endswith('.'):
        basename = f'{basename}pdf'
    dest_key = f'{subpath}/leg_{row.legacy_id}_{basename}'

    if dry_run:
        return f'/{dest_key}', 'Baixar anexo (legado)', True, False

    if default_storage.exists(dest_key):
        return default_storage.url(dest_key), 'Baixar anexo (legado)', True, False

    with src.open('rb') as handle:
        saved = default_storage.save(dest_key, File(handle))
    return default_storage.url(saved), 'Baixar anexo (legado)', True, False


def _get_or_create_pasta(config: MigracaoConfig) -> PastaDocumento | None:
    nome = str(_cfg_legislativo(config).get('pasta_nome', 'Legislativo (legado)')).strip()
    pasta, _ = PastaDocumento.objects.get_or_create(
        nome=nome,
        parent=None,
        defaults={'icone': 'scale', 'cor': '#10b981'},
    )
    return pasta


def _get_tipo_documento(config: MigracaoConfig, natureza: str) -> TipoDocumento:
    mapa = _mapa_natureza(config)
    slug = mapa.get(natureza.strip())
    if not slug:
        for key, val in mapa.items():
            if key.lower() == natureza.strip().lower():
                slug = val
                break
    if not slug:
        slug = str(_cfg_legislativo(config).get('tipo_documento_slug_padrao', 'generico'))
    tipo = TipoDocumento.objects.filter(slug=slug).first()
    if tipo is None:
        tipo = TipoDocumento.objects.filter(slug='generico').first()
    if tipo is None:
        raise ValueError('Nenhum TipoDocumento disponível no tenant (rode seed de documentos).')
    return tipo


def _etiquetas_para(row: LegislativoLegado) -> list[EtiquetaDocumento]:
    tags: list[EtiquetaDocumento] = []
    legado, _ = EtiquetaDocumento.objects.get_or_create(
        nome='Legado CMMC',
        defaults={'cor': '#6b7280'},
    )
    tags.append(legado)
    if row.natureza.strip():
        nat, _ = EtiquetaDocumento.objects.get_or_create(
            nome=row.natureza.strip()[:120],
            defaults={'cor': '#3b82f6'},
        )
        tags.append(nat)
    if row.stts.strip():
        st, _ = EtiquetaDocumento.objects.get_or_create(
            nome=f'Status: {row.stts.strip()[:100]}',
            defaults={'cor': '#f59e0b'},
        )
        tags.append(st)
    return tags


def _exportar_csv(rows: list[LegislativoLegado], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                'id',
                'num',
                'ano',
                'assunto',
                'processo',
                'natureza',
                'solic',
                'dest',
                'obs',
                'stts',
                'link',
            ],
        )
        for row in rows:
            writer.writerow(
                [
                    row.legacy_id,
                    row.num,
                    row.ano,
                    row.assunto,
                    row.processo,
                    row.natureza,
                    row.solic,
                    row.dest,
                    row.obs,
                    row.stts,
                    row.link,
                ],
            )


@transaction.atomic
def _importar_um(
    row: LegislativoLegado,
    *,
    config: MigracaoConfig,
    autor: User,
    pasta: PastaDocumento | None,
    dry_run: bool,
) -> tuple[bool, bool, bool, bool]:
    """Retorna (criou, copiou_arquivo, arquivo_ausente, http_link)."""
    url, rotulo, copiou, ausente = _resolver_link(row, config, dry_run=dry_run)
    http = bool((row.link or '').strip().startswith('http'))
    if dry_run:
        return True, copiou, ausente, http

    tipo = _get_tipo_documento(config, row.natureza)
    status = _status_documento(row.stts)
    doc = Documento.objects.create(
        titulo=_titulo(row)[:500],
        tipo_documento=tipo,
        pasta=pasta,
        conteudo=_montar_conteudo_html(row, link_anexo=url, link_rotulo=rotulo),
        autor=autor,
        status=status,
        versao_atual=1,
    )
    if status == Documento.Status.FINALIZADO:
        Documento.objects.filter(pk=doc.pk).update(finalizado_em=timezone.now())

    doc.etiquetas.set(_etiquetas_para(row))

    MigracaoLegadoRef.objects.create(
        tipo=TIPO_REF,
        legacy_id=row.legacy_id,
        gabtech_id=doc.pk,
        meta={
            'num': row.num,
            'ano': row.ano,
            'natureza': row.natureza,
            'stts': row.stts,
            'link': row.link,
        },
    )
    return True, copiou, ausente, http


def executar_fase5_legislativo(
    config: MigracaoConfig,
    *,
    dry_run: bool = True,
    limit: int | None = None,
    repo_root: Path | None = None,
) -> ResultadoFase5:
    res = ResultadoFase5(dry_run=dry_run)
    leg_cfg = _cfg_legislativo(config)
    modo = str(leg_cfg.get('modo', 'skip')).strip().lower()

    if modo in ('skip', ''):
        res.pulados_modo = 1
        res.erros.append(
            f'legislativo.modo={modo!r} — defina documentos_gabtech ou metadados_csv no YAML.',
        )
        return res
    if modo == 'fase_5':
        modo = 'documentos_gabtech'

    sql_text = ler_sql(config.sql_path)
    rows = iter_legislativo(sql_text)
    res.total_legado = len(rows)
    if limit is not None:
        rows = rows[:limit]

    if modo == 'metadados_csv':
        rel = str(leg_cfg.get('csv_saida', 'deploy/migracao/edsonsantos-legislativo.csv'))
        out = Path(rel)
        if not out.is_absolute() and repo_root is not None:
            out = repo_root / out
        if not dry_run:
            _exportar_csv(rows, out)
            res.csv_path = str(out)
        else:
            res.csv_path = f'(dry-run) {out}'
        res.criados = len(rows)
        return res

    if modo != 'documentos_gabtech':
        res.erros.append(f'Modo legislativo desconhecido: {modo}')
        return res

    existentes = set(
        MigracaoLegadoRef.objects.filter(tipo=TIPO_REF).values_list('legacy_id', flat=True),
    )

    autor = User.objects.filter(email__iexact=config.default_responsavel_email).first()
    if autor is None:
        res.erros.append(f'Autor padrão não encontrado: {config.default_responsavel_email}')
        return res

    pasta = None if dry_run else _get_or_create_pasta(config)

    for row in rows:
        if row.legacy_id in existentes:
            res.ja_importados += 1
            continue
        try:
            criou, copiou, ausente, http = _importar_um(
                row,
                config=config,
                autor=autor,
                pasta=pasta,
                dry_run=dry_run,
            )
            if criou:
                res.criados += 1
            if copiou:
                res.arquivos_copiados += 1
            if ausente and (row.link or '').strip() and not http:
                res.arquivos_ausentes += 1
            if http:
                res.links_http += 1
            if not (row.link or '').strip():
                res.sem_link += 1
        except Exception as exc:
            res.erros.append(f'leg {row.legacy_id}: {exc}')

    return res
