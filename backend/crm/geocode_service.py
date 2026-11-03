"""
Geocodificação de endereços brasileiros com fallbacks gratuitos (OSM / Photon / Open-Meteo).
"""

from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

USER_AGENT = 'GabTech-Gabinete/1.0 (crm-geocode)'


@dataclass
class GeocodeResult:
    latitude: float
    longitude: float
    precisao: str  # endereco | bairro | municipio


def normalizar_endereco(data: dict[str, Any]) -> dict[str, str]:
    estado = (data.get('estado') or '').strip()
    if len(estado) > 2:
        estado = estado[:2]
    estado = estado.upper()

    return {
        'logradouro': (data.get('logradouro') or '').strip(),
        'numero': (data.get('numero') or '').strip(),
        'bairro': (data.get('bairro') or '').strip(),
        'cidade': (data.get('cidade') or '').strip(),
        'estado': estado,
        'cep': re.sub(r'\D', '', data.get('cep') or ''),
    }


def _http_get_json(url: str) -> Any:
    req = urllib.request.Request(
        url,
        headers={
            'Accept': 'application/json',
            'Accept-Language': 'pt-BR',
            'User-Agent': USER_AGENT,
        },
        method='GET',
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.loads(response.read().decode())


def _nominatim(
    *,
    q: str | None = None,
    structured: dict[str, str] | None = None,
) -> GeocodeResult | None:
    params: dict[str, str] = {
        'format': 'json',
        'limit': '1',
        'countrycodes': 'br',
    }
    if q:
        params['q'] = q
    if structured:
        for key, value in structured.items():
            if value:
                params[key] = value

    url = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode(params)
    try:
        results = _http_get_json(url)
        if not results:
            return None
        hit = results[0]
        return GeocodeResult(
            latitude=float(hit['lat']),
            longitude=float(hit['lon']),
            precisao='endereco',
        )
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError) as exc:
        logger.debug('Nominatim indisponível ou sem resultado: %s', exc)
        return None


def _photon(query: str) -> GeocodeResult | None:
    params = urllib.parse.urlencode({'q': query, 'limit': 1, 'lang': 'pt'})
    url = f'https://photon.komoot.io/api/?{params}'
    try:
        data = _http_get_json(url)
        features = data.get('features') or []
        if not features:
            return None
        lon, lat = features[0]['geometry']['coordinates'][:2]
        return GeocodeResult(latitude=float(lat), longitude=float(lon), precisao='endereco')
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError) as exc:
        logger.debug('Photon indisponível ou sem resultado: %s', exc)
        return None


def _open_meteo_municipio(cidade: str, estado: str) -> GeocodeResult | None:
    busca = cidade.strip()
    if estado:
        busca = f'{busca}, {estado}'
    params = urllib.parse.urlencode(
        {
            'name': busca,
            'count': 1,
            'language': 'pt',
            'format': 'json',
            'countryCode': 'BR',
        }
    )
    url = f'https://geocoding-api.open-meteo.com/v1/search?{params}'
    try:
        data = _http_get_json(url)
        results = data.get('results') or []
        if not results:
            return None
        hit = results[0]
        return GeocodeResult(
            latitude=float(hit['latitude']),
            longitude=float(hit['longitude']),
            precisao='municipio',
        )
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError) as exc:
        logger.debug('Open-Meteo indisponível ou sem resultado: %s', exc)
        return None


def _join_endereco(*partes: str | None) -> str:
    return ', '.join(p for p in partes if p)


def geocodificar_endereco(endereco: dict[str, Any]) -> GeocodeResult | None:
    """
    Tenta, em ordem: Nominatim → Photon (endereço) → Photon (bairro) → Open-Meteo (município).
    """
    e = normalizar_endereco(endereco)

    tem_minimo = bool(e['cidade'] or e['cep'] or (e['logradouro'] and e['bairro']))
    if not tem_minimo:
        return None

    rua = e['logradouro']
    if rua and e['numero']:
        rua = f'{rua} {e["numero"]}'

    completo = _join_endereco(rua, e['bairro'], e['cidade'], e['estado'], e['cep'] or None, 'Brasil')
    sem_numero = _join_endereco(e['logradouro'], e['bairro'], e['cidade'], e['estado'], e['cep'] or None, 'Brasil')
    bairro_cidade = _join_endereco(e['bairro'], e['cidade'], e['estado'], 'Brasil')
    cep_br = _join_endereco(e['cep'], 'Brasil') if e['cep'] else ''

    # 1) Nominatim — uma chamada por requisição (política de uso OSM)
    hit: GeocodeResult | None = None
    if e['cidade'] and e['logradouro']:
        hit = _nominatim(
            structured={
                'street': rua or e['logradouro'],
                'city': e['cidade'],
                'state': e['estado'],
                'postalcode': e['cep'],
                'country': 'Brazil',
            }
        )
    elif cep_br:
        hit = _nominatim(q=cep_br)
    elif completo:
        hit = _nominatim(q=completo)
    if hit:
        return hit

    # 2) Photon — endereço completo
    for query in (completo, sem_numero):
        if not query:
            continue
        hit = _photon(query)
        if hit:
            return hit

    # 3) Photon — centro aproximado do bairro / região
    if bairro_cidade and e['bairro']:
        hit = _photon(bairro_cidade)
        if hit:
            hit.precisao = 'bairro'
            return hit

    # 4) Open-Meteo — centro do município
    if e['cidade']:
        hit = _open_meteo_municipio(e['cidade'], e['estado'])
        if hit:
            return hit

    return None
