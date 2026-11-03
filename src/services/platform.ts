import { ApiError, getPlatformApiBaseUrl } from '@/services/api'
import type { LogoFormato } from '@/constants/logoIdentidade'

export type CadastroGabineteStatus =
  | 'pendente'
  | 'processando'
  | 'concluido'
  | 'falhou'

export interface CadastroGabineteResposta {
  id: string
  status: CadastroGabineteStatus
  slug: string
  nome_gabinete: string
  logo?: string
  logo_formato?: LogoFormato
  schema_name: string
  domain: string
  admin_email: string
  erro_mensagem: string
  created_at: string
  concluido_em: string | null
  login_url: string | null
  api_base_url: string | null
  app_url_sugerida: string | null
}

export interface CadastroGabinetePayload {
  nome_gabinete: string
  slug: string
  admin_nome: string
  admin_email: string
  admin_senha: string
  admin_senha_confirmacao: string
  aceite_termos: boolean
  codigo_convite?: string
  logo?: string
  logo_formato?: LogoFormato
}

async function platformFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const base = getPlatformApiBaseUrl()
  const url = `${base}/${path.replace(/^\//, '')}`
  const headers = new Headers(init?.headers)
  if (init?.body !== undefined && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(url, { ...init, headers })
  const text = await response.text()
  let data: unknown = null
  if (text) {
    try {
      data = JSON.parse(text)
    } catch {
      data = text
    }
  }

  if (!response.ok) {
    let message = 'Erro na requisição'
    if (typeof data === 'object' && data !== null) {
      const record = data as Record<string, unknown>
      if (record.detail != null) {
        message = String(record.detail)
      } else {
        for (const [field, value] of Object.entries(record)) {
          if (Array.isArray(value) && value.length > 0) {
            message = `${field.replace(/_/g, ' ')}: ${String(value[0])}`
            break
          }
        }
      }
    }
    throw new ApiError(message, response.status, data)
  }

  return data as T
}

export async function criarCadastroGabinete(
  payload: CadastroGabinetePayload,
): Promise<CadastroGabineteResposta> {
  return platformFetch<CadastroGabineteResposta>('api/platform/cadastro-gabinete/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function consultarCadastroGabinete(id: string): Promise<CadastroGabineteResposta> {
  return platformFetch<CadastroGabineteResposta>(`api/platform/cadastro-gabinete/${id}/`)
}
