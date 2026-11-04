from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class MigracaoConfig:
    raw: dict[str, Any]
    repo_root: Path

    @property
    def schema_name(self) -> str:
        return str(self.raw['tenant']['schema_name'])

    @property
    def sql_path(self) -> Path:
        rel = self.raw['fonte']['sql_path']
        p = Path(rel)
        return p if p.is_absolute() else self.repo_root / p

    @property
    def importar_stts_cadastro(self) -> set[int]:
        return set(int(x) for x in self.raw['cadastro']['importar_stts'])

    @property
    def deduplicar_cpf(self) -> bool:
        return bool(self.raw['cadastro'].get('deduplicar_cpf', True))

    @property
    def batch_size_cadastro(self) -> int:
        return int(self.raw['execucao'].get('batch_size_cadastro', 500))

    @property
    def importar_stts_atendimento(self) -> set[int]:
        return set(int(x) for x in self.raw['atendimento']['importar_stts'])

    @property
    def mapear_stts_atendimento(self) -> dict[int, str]:
        raw = self.raw['atendimento']['mapear_stts']
        return {int(k): str(v) for k, v in raw.items()}

    @property
    def orfaos_vcad(self) -> str:
        return str(self.raw['atendimento'].get('orfaos_vcad', 'criar_cidadao_placeholder'))

    @property
    def placeholder_nome(self) -> str:
        return str(self.raw['atendimento'].get('placeholder_nome', 'Munícipe (cadastro legado ausente)'))

    @property
    def canal_como_tag(self) -> bool:
        return bool(self.raw['atendimento'].get('canal_como_tag', True))

    @property
    def html_descricao(self) -> str:
        return str(self.raw['atendimento'].get('html_descricao', 'sanitizar'))

    @property
    def default_responsavel_email(self) -> str:
        return str(self.raw['usuarios_legado']['default_responsavel_email'])

    @property
    def mapa_usuarios_legado(self) -> dict[str, str | None]:
        return dict(self.raw['usuarios_legado'].get('mapa', {}))

    @property
    def usuarios_provisionamento(self) -> dict[str, Any]:
        raw = self.raw.get('usuarios_legado', {}).get('provisionamento', {})
        return raw if isinstance(raw, dict) else {}

    @property
    def macrotema_default(self) -> str:
        return str(self.raw['macrotemas']['default'])

    @property
    def macrotema_por_vsecr(self) -> dict[int, str]:
        raw = self.raw['macrotemas'].get('por_vsecr', {})
        return {int(k): str(v) for k, v in raw.items()}

    @property
    def macrotema_por_categoria(self) -> dict[int, str]:
        raw = self.raw['macrotemas'].get('por_categoria_id', {})
        return {int(k): str(v) for k, v in raw.items()}

    @property
    def batch_size_atendimento(self) -> int:
        return int(self.raw['execucao'].get('batch_size_atendimento', 200))

    @property
    def agenda_importar(self) -> bool:
        return bool(self.raw.get('agenda', {}).get('importar', True))

    @property
    def agenda_tipo_evento_por_tag(self) -> dict[str, dict]:
        raw = self.raw.get('agenda', {}).get('tipo_evento_por_tag', {})
        return {str(k): dict(v) if v else {} for k, v in raw.items()}

    @property
    def agenda_status_por_stts(self) -> dict[str, str]:
        raw = self.raw.get('agenda', {}).get('status_por_stts', {})
        return {str(k): str(v) for k, v in raw.items()}

    @property
    def media_legacy_root(self) -> Path | None:
        raw = self.raw.get('fonte', {}).get('media_legacy_root')
        if raw is None or str(raw).strip() in ('', 'null', 'None'):
            return None
        p = Path(str(raw))
        return p if p.is_absolute() else self.repo_root / p

    @property
    def anexos_importar(self) -> bool:
        return bool(self.raw.get('anexos', {}).get('importar', True))

    @property
    def anexos_se_arquivo_ausente(self) -> str:
        return str(self.raw.get('anexos', {}).get('se_arquivo_ausente', 'registrar_log'))

    @property
    def anexos_subpastas_busca(self) -> list[str]:
        raw = self.raw.get('anexos', {}).get('subpastas_busca', ['uploads', 'files', 'media'])
        return [str(x) for x in raw]

    @property
    def anexos_mapa_tipo_cadastro(self) -> dict[str, str]:
        defaults = {
            'Curriculo': 'curriculo',
            'Curriculum': 'curriculo',
            'Documento': 'documento_pessoal',
        }
        raw = self.raw.get('anexos', {}).get('mapa_tipo_cadastro', {})
        merged = {**defaults, **{str(k): str(v) for k, v in raw.items()}}
        return merged


def carregar_config(path: Path, repo_root: Path) -> MigracaoConfig:
    data = yaml.safe_load(path.read_text(encoding='utf-8'))
    return MigracaoConfig(raw=data, repo_root=repo_root)
