/**
 * Cliente HTTP base — injeta Authorization Bearer quando há token no localStorage.
 */

const TOKEN_KEY = 'token'
export const TENANT_API_STORAGE_KEY = 'gabtech_api_base'

/** API do schema public (cadastro de gabinetes). */
export function getPlatformApiBaseUrl(): string {
  const env = import.meta.env.VITE_PLATFORM_API_BASE_URL as string | undefined
  if (env?.trim()) {
    return env.replace(/\/$/, '')
  }
  const port = (import.meta.env.VITE_API_PORT as string | undefined) ?? '8800'
  if (typeof window !== 'undefined') {
    const { protocol, hostname } = window.location
    // localhost mapeado a tenant no dev — 127.0.0.1 cai no schema public
    const host = hostname === 'localhost' ? '127.0.0.1' : hostname
    return `${protocol}//${host}:${port}`
  }
  return 'http://127.0.0.1:8800'
}

export function setTenantApiBaseUrl(url: string): void {
  localStorage.setItem(TENANT_API_STORAGE_KEY, url.replace(/\/$/, ''))
}

/** Host de tenant no dev (*.localhost, exceto host nu "localhost"). */
export function tenantHostnameFromBrowser(): string | null {
  if (typeof window === 'undefined') {
    return null
  }
  const { hostname } = window.location
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return null
  }
  if (hostname.includes('.') && hostname.endsWith('.localhost')) {
    return hostname
  }
  return null
}

/** Alinha localStorage com o host atual (demo em localhost ou tenant *.localhost). */
export function syncTenantApiBaseFromBrowser(): void {
  if (typeof window === 'undefined') {
    return
  }
  const port = (import.meta.env.VITE_API_PORT as string | undefined) ?? '8800'
  const { protocol, hostname } = window.location
  const tenantHost = tenantHostnameFromBrowser()
  if (tenantHost) {
    setTenantApiBaseUrl(`${protocol}//${tenantHost}:${port}`)
    return
  }
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    setTenantApiBaseUrl(`${protocol}//${hostname}:${port}`)
  }
}

/** API do tenant atual (login e módulos do gabinete). */
export function resolveTenantApiBaseUrl(): string {
  const env = import.meta.env.VITE_API_BASE_URL as string | undefined
  if (env?.trim()) {
    return env.replace(/\/$/, '')
  }
  if (typeof window !== 'undefined') {
    const port = (import.meta.env.VITE_API_PORT as string | undefined) ?? '8800'
    const { hostname, protocol } = window.location
    const tenantHost = tenantHostnameFromBrowser()
    if (tenantHost) {
      return `${protocol}//${tenantHost}:${port}`
    }
    // localhost = tenant demo (domínio cadastrado); não reutilizar API de outro gabinete no localStorage
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return `${protocol}//${hostname}:${port}`
    }
    const stored = localStorage.getItem(TENANT_API_STORAGE_KEY)
    if (stored?.trim()) {
      return stored.replace(/\/$/, '')
    }
  }
  return 'http://demo.localhost:8800'
}

export function getApiBaseUrl(): string {
  return resolveTenantApiBaseUrl()
}

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

function extractApiErrorMessage(data: unknown): string {
  if (typeof data !== 'object' || data === null) {
    return 'Erro na requisição'
  }
  const record = data as Record<string, unknown>
  if ('detail' in record && record.detail != null) {
    return String(record.detail)
  }
  if (Array.isArray(record.non_field_errors) && record.non_field_errors[0]) {
    return String(record.non_field_errors[0])
  }
  for (const [field, value] of Object.entries(record)) {
    if (Array.isArray(value) && value.length > 0) {
      const label = field.replace(/_/g, ' ')
      return `${label}: ${String(value[0])}`
    }
    if (typeof value === 'string' && value) {
      return value
    }
  }
  return 'Erro na requisição'
}

export class ApiError extends Error {
  status: number
  data: unknown

  constructor(message: string, status: number, data: unknown = null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

export type ApiFetchOptions = RequestInit & {
  /** Não envia Authorization (ex.: login) */
  skipAuth?: boolean
  /** Parse JSON automaticamente (padrão: true) */
  parseJson?: boolean
}

export async function apiFetch<T = unknown>(
  path: string,
  options: ApiFetchOptions = {},
): Promise<T> {
  const { skipAuth = false, parseJson = true, headers: initHeaders, ...rest } = options

  const headers = new Headers(initHeaders)

  if (rest.body !== undefined && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  if (!skipAuth) {
    const token = getStoredToken()
    if (token && !headers.has('Authorization')) {
      headers.set('Authorization', `Bearer ${token}`)
    }
  }

  const base = resolveTenantApiBaseUrl()
  const url = path.startsWith('http') ? path : `${base}/${path.replace(/^\//, '')}`

  const response = await fetch(url, {
    ...rest,
    headers,
  })

  if (!parseJson) {
    if (!response.ok) {
      throw new ApiError(response.statusText || 'Erro na requisição', response.status)
    }
    return undefined as T
  }

  let data: unknown = null
  const text = await response.text()
  if (text) {
    try {
      data = JSON.parse(text)
    } catch {
      data = text
    }
  }

  if (!response.ok) {
    const message = extractApiErrorMessage(data)
    throw new ApiError(message, response.status, data)
  }

  return data as T
}

/** Upload multipart (não define Content-Type — o browser inclui o boundary). */
export async function apiUpload<T = unknown>(
  path: string,
  formData: FormData,
): Promise<T> {
  const token = getStoredToken()
  const headers = new Headers()
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const base = resolveTenantApiBaseUrl()
  const url = path.startsWith('http') ? path : `${base}/${path.replace(/^\//, '')}`
  const response = await fetch(url, {
    method: 'POST',
    headers,
    body: formData,
  })

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
    const message =
      typeof data === 'object' && data !== null && 'detail' in data
        ? String((data as { detail: unknown }).detail)
        : typeof data === 'object' && data !== null && 'arquivo' in data
          ? String((data as { arquivo: unknown[] }).arquivo[0])
          : 'Erro no upload'
    throw new ApiError(message, response.status, data)
  }

  return data as T
}

/** Download autenticado (retorna Blob). */
export async function apiDownload(path: string): Promise<Blob> {
  const token = getStoredToken()
  const headers = new Headers()
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const base = resolveTenantApiBaseUrl()
  const url = path.startsWith('http') ? path : `${base}/${path.replace(/^\//, '')}`
  const response = await fetch(url, { headers })

  if (!response.ok) {
    throw new ApiError(response.statusText || 'Erro ao baixar arquivo', response.status)
  }

  return response.blob()
}
