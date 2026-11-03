from __future__ import annotations

from dataclasses import dataclass

from core.legado.sql_parse import parse_mysql_value_list


@dataclass
class CadastroDocLegado:
    legacy_id: int
    v_cad: int
    data: str
    tipo: str
    descr: str
    arquivo: str


@dataclass
class AtendimentoDocLegado:
    legacy_id: int
    v_atend: int
    tipo: int
    data: str
    descr: str
    arquivo: str


def iter_cadastro_docs(sql_text: str) -> list[CadastroDocLegado]:
    rows: list[CadastroDocLegado] = []
    in_block = False
    for line in sql_text.split('\n'):
        if 'INSERT INTO `tbCadastroDocs`' in line:
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
        if len(vals) != 6:
            continue
        rows.append(
            CadastroDocLegado(
                legacy_id=int(vals[0]),
                v_cad=int(vals[1]),
                data=str(vals[2]),
                tipo=str(vals[3]).strip(),
                descr=str(vals[4]).strip(),
                arquivo=str(vals[5]).strip(),
            ),
        )
    return rows


def iter_atendimento_docs(sql_text: str) -> list[AtendimentoDocLegado]:
    rows: list[AtendimentoDocLegado] = []
    in_block = False
    for line in sql_text.split('\n'):
        if 'INSERT INTO `tbAtendimentoDocs`' in line:
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
        if len(vals) != 6:
            continue
        rows.append(
            AtendimentoDocLegado(
                legacy_id=int(vals[0]),
                v_atend=int(vals[1]),
                tipo=int(vals[2]),
                data=str(vals[3]),
                descr=str(vals[4]).strip(),
                arquivo=str(vals[5]).strip(),
            ),
        )
    return rows
