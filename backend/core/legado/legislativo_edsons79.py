from __future__ import annotations

from dataclasses import dataclass

from core.legado.cadastro_edsons79 import ler_sql
from core.legado.sql_parse import parse_mysql_value_list


@dataclass(frozen=True)
class LegislativoLegado:
    legacy_id: int
    num: str
    ano: str
    assunto: str
    processo: str
    natureza: str
    solic: str
    dest: str
    obs: str
    stts: str
    link: str


def iter_legislativo(sql_text: str) -> list[LegislativoLegado]:
    rows: list[LegislativoLegado] = []
    in_block = False
    for line in sql_text.split('\n'):
        if 'INSERT INTO `tbLegislativo`' in line:
            in_block = True
            continue
        if in_block and line.strip().startswith('INSERT INTO `') and 'tbLegislativo' not in line:
            in_block = False
        if not in_block:
            continue
        stripped = line.strip().rstrip(',')
        if not stripped.startswith('('):
            continue
        vals = parse_mysql_value_list(stripped)
        if len(vals) != 11:
            continue
        rows.append(
            LegislativoLegado(
                legacy_id=int(vals[0]),
                num=str(vals[1]).strip(),
                ano=str(vals[2]).strip(),
                assunto=str(vals[3]).strip(),
                processo=str(vals[4]).strip(),
                natureza=str(vals[5]).strip(),
                solic=str(vals[6]).strip(),
                dest=str(vals[7]).strip(),
                obs=str(vals[8]).strip(),
                stts=str(vals[9]).strip(),
                link=str(vals[10]).strip(),
            ),
        )
    return rows


def carregar_legislativo(sql_path) -> list[LegislativoLegado]:
    return iter_legislativo(ler_sql(sql_path))
