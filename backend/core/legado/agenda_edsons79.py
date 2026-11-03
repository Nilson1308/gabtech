from __future__ import annotations

from dataclasses import dataclass

from core.legado.sql_parse import parse_mysql_value_list

# Cor de fundo legada (`stts`) quando `tag` vem vazia
STTS_COR_PARA_TAG: dict[str, str] = {
    '#DCF8F9': 'Evento',
    '#F0F0F0': 'Geral',
    '#FFC8FF': 'Reunião',
    '#C0E8FF': 'Atendimento Gabinete',
    '#E1FFE1': 'Exame/Consulta',
    '#FFC8C8': 'Cancelado',
    '#FFE1AF': 'Inauguração',
    '#FFFFE1': 'Aguardando Confirmação',
}


@dataclass
class EventoLegado:
    legacy_id: int
    titulo: str
    inicio: str
    termino: str
    local: str
    endereco: str
    convite: str
    ref: str
    fone: str
    stts: str
    tag: str


def iter_eventos(sql_text: str) -> list[EventoLegado]:
    rows: list[EventoLegado] = []
    in_block = False
    for line in sql_text.split('\n'):
        if 'INSERT INTO `tbEventos`' in line and 'bkp' not in line.lower():
            in_block = True
            continue
        if in_block and line.strip().startswith('INSERT INTO `'):
            if 'tbEventos' not in line or 'bkp' in line.lower():
                in_block = False
        if not in_block:
            continue
        stripped = line.strip().rstrip(',')
        if not stripped.startswith('('):
            continue
        vals = parse_mysql_value_list(stripped)
        if len(vals) != 11:
            raise ValueError(
                f'Evento id={vals[0] if vals else "?"}: esperado 11 campos, veio {len(vals)}',
            )
        rows.append(
            EventoLegado(
                legacy_id=int(vals[0]),
                titulo=str(vals[1]).strip(),
                inicio=str(vals[2]).strip(),
                termino=str(vals[3]).strip(),
                local=str(vals[4]).strip(),
                endereco=str(vals[5]).strip(),
                convite=str(vals[6]).strip(),
                ref=str(vals[7]).strip(),
                fone=str(vals[8]).strip(),
                stts=str(vals[9]).strip(),
                tag=str(vals[10]).strip(),
            ),
        )
    return rows


def nome_tipo_evento(row: EventoLegado) -> str:
    if row.tag:
        return row.tag[:120]
    if row.stts in STTS_COR_PARA_TAG:
        return STTS_COR_PARA_TAG[row.stts][:120]
    return 'Geral'


def montar_descricao_evento(row: EventoLegado) -> str:
    partes = [f'[legado:evento:{row.legacy_id}]']
    for label, val in (
        ('Local', row.local),
        ('Endereço', row.endereco),
        ('Convite', row.convite),
        ('Referência', row.ref),
        ('Telefone', row.fone),
    ):
        if val:
            partes.append(f'{label}: {val}')
    return '\n'.join(partes).strip()[:8000]
