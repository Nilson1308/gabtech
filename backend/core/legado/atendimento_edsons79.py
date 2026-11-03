from __future__ import annotations

import re
from dataclasses import dataclass

from core.legado.cadastro_edsons79 import ler_sql
from core.legado.sql_parse import parse_mysql_value_list


@dataclass
class CategoriaAtendimentoLegado:
    legacy_id: int
    v_secr: int
    nome: str


@dataclass
class AtendimentoLegado:
    legacy_id: int
    v_usu: int
    v_cad: int
    v_cat: int
    dt_ini: str
    dt_enc: str
    descr: str
    stts: int
    tipo: str


def iter_atendimentos(sql_text: str) -> list[AtendimentoLegado]:
    rows: list[AtendimentoLegado] = []
    in_block = False
    for line in sql_text.split('\n'):
        if 'INSERT INTO `tbAtendimento`' in line:
            in_block = True
            continue
        if in_block and line.strip().startswith('INSERT INTO `'):
            in_block = False
        if not in_block:
            continue
        stripped = line.strip().rstrip(',')
        if not stripped.startswith('('):
            continue
        vals = parse_mysql_value_list(stripped)
        if len(vals) != 9:
            raise ValueError(
                f'Atendimento id={vals[0] if vals else "?"}: esperado 9 campos, veio {len(vals)}',
            )
        rows.append(
            AtendimentoLegado(
                legacy_id=int(vals[0]),
                v_usu=int(vals[1]),
                v_cad=int(vals[2]),
                v_cat=int(vals[3]),
                dt_ini=str(vals[4]),
                dt_enc=str(vals[5]),
                descr=str(vals[6]),
                stts=int(vals[7]),
                tipo=str(vals[8]).strip(),
            ),
        )
    return rows


def carregar_categorias_atendimento(sql_text: str) -> dict[int, CategoriaAtendimentoLegado]:
    out: dict[int, CategoriaAtendimentoLegado] = {}
    in_block = False
    for line in sql_text.split('\n'):
        if 'INSERT INTO `tbAtendimentoCat`' in line:
            in_block = True
            continue
        if in_block and line.strip().startswith('INSERT INTO `'):
            in_block = False
        if not in_block:
            continue
        stripped = line.strip().rstrip(',')
        if not stripped.startswith('('):
            continue
        vals = parse_mysql_value_list(stripped)
        if len(vals) != 3:
            continue
        cat = CategoriaAtendimentoLegado(
            legacy_id=int(vals[0]),
            v_secr=int(vals[1]),
            nome=str(vals[2]).strip(),
        )
        out[cat.legacy_id] = cat
    return out


def extrair_assunto(categorias: dict[int, CategoriaAtendimentoLegado], v_cat: int) -> str:
    cat = categorias.get(v_cat)
    if cat and cat.nome:
        return cat.nome[:255]
    return f'Categoria legado #{v_cat}'[:255]
