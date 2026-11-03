"""Parâmetros do formulário público de credenciamento por evento."""

from __future__ import annotations

from typing import Any


def default_credenciamento_config() -> dict[str, Any]:
    return {
        'mostrar_email': True,
        'mostrar_data_nascimento': True,
        'mostrar_orgao_instituicao': True,
        'url_politica_privacidade': '',
    }


def normalize_credenciamento_config(raw: dict[str, Any] | None) -> dict[str, Any]:
    base = default_credenciamento_config()
    if not raw or not isinstance(raw, dict):
        return base
    merged = {**base, **raw}
    merged['mostrar_email'] = bool(merged.get('mostrar_email', True))
    merged['mostrar_data_nascimento'] = bool(merged.get('mostrar_data_nascimento', True))
    merged['mostrar_orgao_instituicao'] = bool(merged.get('mostrar_orgao_instituicao', True))
    url = merged.get('url_politica_privacidade') or ''
    merged['url_politica_privacidade'] = str(url).strip()[:500]
    return merged
