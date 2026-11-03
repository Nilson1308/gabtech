import type { Endereco } from '@/types'
import { apiFetch } from '@/services/api'

export interface Coordenadas {
  latitude: number
  longitude: number
}

/** Máximo 6 casas decimais (igual ao DecimalField do backend). */
export function arredondarCoordenada(valor: number | null | undefined): number | null {
  if (valor == null || !Number.isFinite(valor)) return null
  return Math.round(valor * 1_000_000) / 1_000_000
}

export type PrecisaoGeocode = 'endereco' | 'bairro' | 'municipio' | null

export interface ResultadoGeocode extends Coordenadas {
  precisao: PrecisaoGeocode
}

type GeocodeApiResponse = {
  latitude: number | null
  longitude: number | null
  precisao?: PrecisaoGeocode
}

/**
 * Geocodifica endereço via API interna (Nominatim → Photon → Open-Meteo no backend).
 */
export async function geocodificarEndereco(
  endereco: Partial<Endereco>,
): Promise<Coordenadas | null> {
  const resultado = await geocodificarEnderecoDetalhado(endereco)
  return resultado
}

export async function geocodificarEnderecoDetalhado(
  endereco: Partial<Endereco>,
): Promise<ResultadoGeocode | null> {
  const temCampo = [
    endereco.logradouro,
    endereco.bairro,
    endereco.cidade,
    endereco.cep,
  ].some(Boolean)

  if (!temCampo) {
    return null
  }

  try {
    const data = await apiFetch<GeocodeApiResponse>('api/crm/geocode/', {
      method: 'POST',
      body: JSON.stringify({
        logradouro: endereco.logradouro ?? '',
        numero: endereco.numero ?? '',
        bairro: endereco.bairro ?? '',
        cidade: endereco.cidade ?? '',
        estado: endereco.estado ?? '',
        cep: endereco.cep ?? '',
      }),
    })

    if (data.latitude == null || data.longitude == null) {
      return null
    }

    return {
      latitude: arredondarCoordenada(data.latitude)!,
      longitude: arredondarCoordenada(data.longitude)!,
      precisao: data.precisao ?? null,
    }
  } catch {
    return null
  }
}
