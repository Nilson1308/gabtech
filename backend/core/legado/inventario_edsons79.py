"""Inventário estático do dump MySQL edsons79_sys (sem dependência de MySQL)."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class InventarioLegado:
    sql_path: str
    cadastro_total: int = 0
    cadastro_stts: dict[str, int] = field(default_factory=dict)
    cadastro_cpf_preenchido: int = 0
    cadastro_cpf_vazio: int = 0
    cadastro_cpf_duplicados: int = 0
    atendimento_total: int = 0
    atendimento_stts: dict[str, int] = field(default_factory=dict)
    atendimento_orfaos_vcad: int = 0
    atendimento_vusu: dict[str, int] = field(default_factory=dict)
    categorias_total: int = 0
    eventos_total: int = 0
    usuarios_legado: dict[str, str] = field(default_factory=dict)
    legislativo_total: int = 0
    cadastro_docs_total: int = 0
    atendimento_docs_total: int = 0
    vcad_tag_total: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


def _extract_insert_rows(text: str, table: str) -> list[str]:
    rows: list[str] = []
    for block in re.finditer(rf"INSERT INTO `{re.escape(table)}`[^;]+;", text, re.DOTALL):
        body = block.group(0)
        idx = body.find('VALUES')
        if idx < 0:
            continue
        chunk = body[idx + 6 :].strip().rstrip(';')
        for part in re.split(r"\),\s*\(", chunk):
            part = part.strip()
            if part.startswith('('):
                part = part[1:]
            if part.endswith(')'):
                part = part[:-1]
            elif part.endswith(');'):
                part = part[:-2]
            if part:
                rows.append(part)
    return rows


def analisar_dump(sql_path: Path) -> InventarioLegado:
    text = sql_path.read_text(encoding='utf-8', errors='replace')
    inv = InventarioLegado(sql_path=str(sql_path.resolve()))

    cad_rows = _extract_insert_rows(text, 'tbCadastro')
    inv.cadastro_total = len(cad_rows)

    cad_ids: set[int] = set()
    cad_stts: Counter[int] = Counter()
    cad_by_cpf: dict[str, list[int]] = defaultdict(list)

    for ch in cad_rows:
        m0 = re.match(r'^(\d+),', ch)
        if not m0:
            continue
        cid = int(m0.group(1))
        cad_ids.add(cid)
        tail = re.search(r', (\d+), (\d+)\s*$', ch)
        if tail:
            cad_stts[int(tail.group(2))] += 1
        qs = re.findall(r"'((?:[^'\\]|\\.)*)'", ch)
        if len(qs) >= 6:
            cpf = qs[5].strip()
            if cpf:
                inv.cadastro_cpf_preenchido += 1
                cad_by_cpf[cpf].append(cid)
            else:
                inv.cadastro_cpf_vazio += 1

    inv.cadastro_stts = {str(k): v for k, v in sorted(cad_stts.items())}
    inv.cadastro_cpf_duplicados = sum(1 for ids in cad_by_cpf.values() if len(ids) > 1)

    at_stts: Counter[int] = Counter()
    at_vusu: Counter[int] = Counter()
    at_total = 0
    at_orphan = 0
    in_at = False
    for line in text.split('\n'):
        if 'INSERT INTO `tbAtendimento`' in line:
            in_at = True
            continue
        if in_at and 'INSERT INTO `' in line and 'tbAtendimento' not in line:
            in_at = False
        if not in_at:
            continue
        line = line.strip().rstrip(',')
        m = re.match(r'^\((\d+), (\d+), (\d+), (\d+),', line)
        if not m:
            continue
        at_total += 1
        vcad = int(m.group(3))
        at_vusu[int(m.group(2))] += 1
        if vcad not in cad_ids:
            at_orphan += 1
        tail = re.search(r", (\d+), '([^']*)'\),?\s*$", line)
        if tail:
            at_stts[int(tail.group(1))] += 1

    inv.atendimento_total = at_total
    inv.atendimento_stts = {str(k): v for k, v in sorted(at_stts.items())}
    inv.atendimento_orfaos_vcad = at_orphan
    inv.atendimento_vusu = {str(k): v for k, v in sorted(at_vusu.items())}

    inv.categorias_total = len(_extract_insert_rows(text, 'tbAtendimentoCat'))

    in_ev = False
    ev_total = 0
    for line in text.split('\n'):
        if 'INSERT INTO `tbEventos`' in line and 'bkp' not in line:
            in_ev = True
            continue
        if 'INSERT INTO `tbEventos-bkp`' in line:
            in_ev = False
        if in_ev and line.strip().startswith('('):
            ev_total += 1
        if in_ev and line.startswith('CREATE TABLE'):
            in_ev = False
    inv.eventos_total = ev_total

    for block in re.finditer(r'INSERT INTO `tbUsuarios`[^;]+;', text, re.DOTALL):
        for u in re.finditer(r"\((\d+), '([^']+)'", block.group(0)):
            inv.usuarios_legado[str(int(u.group(1)))] = u.group(2)

    inv.legislativo_total = len(_extract_insert_rows(text, 'tbLegislativo'))
    inv.cadastro_docs_total = len(_extract_insert_rows(text, 'tbCadastroDocs'))
    inv.atendimento_docs_total = len(_extract_insert_rows(text, 'tbAtendimentoDocs'))
    inv.vcad_tag_total = len(_extract_insert_rows(text, 'tbVCadTag'))

    return inv


def salvar_inventario(inv: InventarioLegado, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(inv.to_dict(), indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
