from __future__ import annotations

import re
from dataclasses import dataclass

from core.legado.cadastro_edsons79 import ler_sql


@dataclass(frozen=True)
class UsuarioLegado:
    legacy_id: int
    login: str
    stts: int


def iter_usuarios(sql_text: str) -> list[UsuarioLegado]:
    rows: list[UsuarioLegado] = []
    for block in re.finditer(r'INSERT INTO `tbUsuarios`[^;]+;', sql_text, re.DOTALL):
        for m in re.finditer(r'\((\d+),\s*\'([^\']*)\',\s*\'[^\']*\',\s*(\d+)\)', block.group(0)):
            rows.append(
                UsuarioLegado(
                    legacy_id=int(m.group(1)),
                    login=str(m.group(2)).strip(),
                    stts=int(m.group(3)),
                ),
            )
    return rows


def carregar_usuarios(sql_path) -> list[UsuarioLegado]:
    return iter_usuarios(ler_sql(sql_path))
