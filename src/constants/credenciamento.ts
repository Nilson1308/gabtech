export interface CredenciamentoConfig {
  mostrar_email: boolean
  mostrar_data_nascimento: boolean
  mostrar_orgao_instituicao: boolean
  url_politica_privacidade: string
}

export const DEFAULT_CREDENCIAMENTO_CONFIG: CredenciamentoConfig = {
  mostrar_email: true,
  mostrar_data_nascimento: true,
  mostrar_orgao_instituicao: true,
  url_politica_privacidade: '',
}

export function normalizeCredenciamentoConfig(
  raw?: Partial<CredenciamentoConfig> | null,
): CredenciamentoConfig {
  return {
    ...DEFAULT_CREDENCIAMENTO_CONFIG,
    ...raw,
    url_politica_privacidade: (raw?.url_politica_privacidade ?? '').trim(),
  }
}

/** URL da política: customizada do evento ou página padrão GabTech. */
export function urlPoliticaPrivacidade(
  config: CredenciamentoConfig,
  eventoId?: string,
): string {
  const custom = config.url_politica_privacidade.trim()
  if (custom) return custom
  const params = new URLSearchParams({ contexto: 'credenciamento' })
  if (eventoId) params.set('evento', eventoId)
  return `${window.location.origin}/privacidade?${params.toString()}`
}
