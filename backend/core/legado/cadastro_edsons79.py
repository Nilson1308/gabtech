from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from core.legado.sql_parse import parse_mysql_value_list


@dataclass
class CadastroLegado:
    legacy_id: int
    data_cad: str
    nome: str
    apelido: str
    tratamento: str
    rg: str
    cpf: str
    sus_sis: str
    cep: str
    logradouro: str
    num: str
    compl: str
    bairro: str
    cidade: str
    uf: str
    celular: str
    telefone: str
    data_nasc: str
    email: str
    instagram: str
    facebook: str
    linkedin: str
    indicado: str
    obs: str
    v_usu: int
    stts: int


def iter_cadastros(sql_text: str) -> list[CadastroLegado]:
    rows: list[CadastroLegado] = []
    in_block = False
    for line in sql_text.split('\n'):
        if 'INSERT INTO `tbCadastro`' in line:
            in_block = 'tbCadastro-old' not in line
            continue
        if in_block and line.strip().startswith('INSERT INTO `'):
            in_block = False
        if not in_block:
            continue
        stripped = line.strip()
        if not stripped.startswith('('):
            continue
        vals = parse_mysql_value_list(stripped.rstrip(','))
        if len(vals) != 26:
            raise ValueError(f'Cadastro id={vals[0] if vals else "?"}: esperado 26 campos, veio {len(vals)}')
        rows.append(
            CadastroLegado(
                legacy_id=int(vals[0]),
                data_cad=str(vals[1]),
                nome=str(vals[2]).strip(),
                apelido=str(vals[3]).strip(),
                tratamento=str(vals[4]).strip(),
                rg=str(vals[5]).strip(),
                cpf=str(vals[6]).strip(),
                sus_sis=str(vals[7]).strip(),
                cep=str(vals[8]).strip(),
                logradouro=str(vals[9]).strip(),
                num=str(vals[10]).strip(),
                compl=str(vals[11]).strip(),
                bairro=str(vals[12]).strip(),
                cidade=str(vals[13]).strip(),
                uf=str(vals[14]).strip(),
                celular=str(vals[15]).strip(),
                telefone=str(vals[16]).strip(),
                data_nasc=str(vals[17]),
                email=str(vals[18]).strip(),
                instagram=str(vals[19]).strip(),
                facebook=str(vals[20]).strip(),
                linkedin=str(vals[21]).strip(),
                indicado=str(vals[22]).strip(),
                obs=str(vals[23]).strip(),
                v_usu=int(vals[24]),
                stts=int(vals[25]),
            ),
        )
    return rows


def carregar_tags_por_cadastro(sql_text: str) -> dict[int, list[str]]:
    tags: dict[int, list[str]] = defaultdict(list)
    in_block = False
    for line in sql_text.split('\n'):
        if 'INSERT INTO `tbVCadTag`' in line:
            in_block = True
            continue
        if in_block and line.strip().startswith('INSERT INTO `'):
            in_block = False
        if not in_block:
            continue
        m = re.match(r"^\((\d+), (\d+), '((?:[^'\\]|\\.)*)'\)", line.strip().rstrip(','))
        if m:
            vcad = int(m.group(2))
            tag = m.group(3).strip()
            if tag and tag not in tags[vcad]:
                tags[vcad].append(tag)
    return dict(tags)


def normalizar_cpf(cpf: str) -> str | None:
    digits = re.sub(r'\D', '', cpf or '')
    if len(digits) != 11:
        return None
    return f'{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}'


def escolher_telefone(celular: str, telefone: str) -> str:
    for raw in (celular, telefone):
        t = (raw or '').strip()
        if t and t not in {'(00) 00000-0000', '(11) 00000-0000', '0', '(11)'}:
            return t[:20]
    return '(sem telefone)'


def parse_data(value: str) -> date | None:
    if not value or value.startswith('0000'):
        return None
    try:
        return datetime.strptime(value[:10], '%Y-%m-%d').date()
    except ValueError:
        return None


def montar_observacoes(row: CadastroLegado) -> str:
    partes = [f'[legado:cad:{row.legacy_id}]']
    if row.indicado:
        partes.append(f'Indicado/ref.: {row.indicado}')
    if row.sus_sis:
        partes.append(f'SUS/SIS: {row.sus_sis}')
    if row.tratamento:
        partes.append(f'Tratamento: {row.tratamento}')
    for label, val in (
        ('Instagram', row.instagram),
        ('Facebook', row.facebook),
        ('LinkedIn', row.linkedin),
    ):
        if val:
            partes.append(f'{label}: {val}')
    if row.obs:
        partes.append(row.obs)
    return '\n\n'.join(partes).strip()[:8000]


def ler_sql(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='replace')
