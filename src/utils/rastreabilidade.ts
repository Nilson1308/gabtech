export type UltimaAcaoTipo = 'criar' | 'alterar' | 'excluir' | null

export interface RastreabilidadeApi {
  criado_em?: string | null
  criado_por_id?: number | null
  criado_por_nome?: string | null
  ultima_acao_em?: string | null
  ultima_acao_por_id?: number | null
  ultima_acao_por_nome?: string | null
  ultima_acao_tipo?: UltimaAcaoTipo
}

export interface Rastreabilidade {
  criadoEm: string | null
  criadoPorNome: string | null
  ultimaAcaoEm: string | null
  ultimaAcaoPorNome: string | null
  ultimaAcaoTipo: UltimaAcaoTipo
}

export function mapRastreabilidade(
  raw?: RastreabilidadeApi | null,
): Rastreabilidade | null {
  if (!raw) return null
  const temAlgo =
    raw.ultima_acao_em ||
    raw.criado_em ||
    raw.ultima_acao_por_nome ||
    raw.criado_por_nome
  if (!temAlgo) return null
  return {
    criadoEm: raw.criado_em ?? null,
    criadoPorNome: raw.criado_por_nome ?? null,
    ultimaAcaoEm: raw.ultima_acao_em ?? null,
    ultimaAcaoPorNome: raw.ultima_acao_por_nome ?? null,
    ultimaAcaoTipo: raw.ultima_acao_tipo ?? null,
  }
}

export function rotuloUltimaAcao(tipo: UltimaAcaoTipo): string {
  switch (tipo) {
    case 'criar':
      return 'Criação'
    case 'alterar':
      return 'Última alteração'
    case 'excluir':
      return 'Exclusão'
    default:
      return 'Última ação'
  }
}
