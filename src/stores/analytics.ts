import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiFetch } from '@/services/api'

// ==================== TIPOS ====================
export interface ProdutividadeAssessor {
  userId: string
  nomeUsuario: string
  concluidos: number
  atrasados: number
  emAndamento: number
  total: number
  taxaSucesso: number
}

export interface AtividadeAuditoria {
  id: string
  tipo: 'ticket_transferido' | 'cidadao_criado' | 'evento_criado' | 'documento_assinado' | 'status_alterado'
  usuario: string
  usuarioId: string
  descricao: string
  timestamp: string
  icone: string
  cor: string
}

export interface GargaloMacrotema {
  macrotema: string
  atrasados: number
  cor: string
}

export interface PinCidadao {
  id: string
  nome: string
  lat: number
  lng: number
  endereco: string
  tags: string[]
}

export type TerritorialAgrupamento = 'macrotema' | 'macrotema_bairro'

export interface MacrotemaFiltroOpcao {
  id: number
  nome: string
  cor: string
}

export interface TerritorialQuery {
  agrupamento?: TerritorialAgrupamento
  macrotemaId?: number | null
  bairro?: string | null
}

export interface ZonaCalor {
  id: string
  nome: string
  bairro?: string
  macrotemaId?: number
  lat: number
  lng: number
  radius: number
  atendimentosPendentes: number
  macrotema: string
  cor: string
}

export interface MapaCentro {
  lat: number
  lng: number
  zoom: number
}

interface ExecutivoApi {
  produtividade: Array<{
    user_id: string
    nome_usuario: string
    concluidos: number
    atrasados: number
    em_andamento: number
    total: number
    taxa_sucesso: number
  }>
  atividades_recentes: Array<{
    id: string
    tipo: AtividadeAuditoria['tipo']
    usuario: string
    usuario_id: string
    descricao: string
    timestamp: string
    icone: string
    cor: string
  }>
  gargalos: Array<{
    macrotema: string
    atrasados: number
    cor: string
  }>
}

interface TerritorialApi {
  pins_cidadaos: Array<{
    id: string
    nome: string
    lat: number
    lng: number
    endereco: string
    tags: string[]
  }>
  zonas_calor: Array<{
    id: string
    nome: string
    bairro?: string
    macrotema_id?: number
    lat: number
    lng: number
    radius: number
    atendimentos_pendentes: number
    macrotema: string
    cor: string
  }>
  centro: MapaCentro
  meta?: {
    agrupamento: TerritorialAgrupamento
    macrotema_id: number | null
    bairro: string
  }
  filtros_disponiveis?: {
    macrotemas: MacrotemaFiltroOpcao[]
    bairros: string[]
  }
}

// ==================== STORE ====================
export const useAnalyticsStore = defineStore('analytics', () => {
  const produtividade = ref<ProdutividadeAssessor[]>([])
  const atividadesRecentes = ref<AtividadeAuditoria[]>([])
  const gargalos = ref<GargaloMacrotema[]>([])
  const pinsCidadaos = ref<PinCidadao[]>([])
  const zonasCalor = ref<ZonaCalor[]>([])
  const mapaCentro = ref<MapaCentro>({ lat: -23.5227, lng: -46.1879, zoom: 12 })
  const territorialAgrupamento = ref<TerritorialAgrupamento>('macrotema')
  const territorialFiltrosMacrotemas = ref<MacrotemaFiltroOpcao[]>([])
  const territorialFiltrosBairros = ref<string[]>([])
  const loading = ref(false)
  const erro = ref<string | null>(null)

  function mapExecutivo(data: ExecutivoApi) {
    produtividade.value = data.produtividade.map(p => ({
      userId: p.user_id,
      nomeUsuario: p.nome_usuario,
      concluidos: p.concluidos,
      atrasados: p.atrasados,
      emAndamento: p.em_andamento,
      total: p.total,
      taxaSucesso: p.taxa_sucesso,
    }))
    atividadesRecentes.value = data.atividades_recentes.map(a => ({
      id: a.id,
      tipo: a.tipo,
      usuario: a.usuario,
      usuarioId: a.usuario_id,
      descricao: a.descricao,
      timestamp: a.timestamp,
      icone: a.icone,
      cor: a.cor,
    }))
    gargalos.value = data.gargalos.map(g => ({
      macrotema: g.macrotema,
      atrasados: g.atrasados,
      cor: g.cor,
    }))
  }

  function mapTerritorial(data: TerritorialApi) {
    pinsCidadaos.value = data.pins_cidadaos.map(p => ({
      id: p.id,
      nome: p.nome,
      lat: p.lat,
      lng: p.lng,
      endereco: p.endereco,
      tags: p.tags,
    }))
    zonasCalor.value = data.zonas_calor.map(z => ({
      id: z.id,
      nome: z.nome,
      bairro: z.bairro || undefined,
      macrotemaId: z.macrotema_id,
      lat: z.lat,
      lng: z.lng,
      radius: z.radius,
      atendimentosPendentes: z.atendimentos_pendentes,
      macrotema: z.macrotema,
      cor: z.cor,
    }))
    mapaCentro.value = data.centro
    if (data.meta?.agrupamento) {
      territorialAgrupamento.value = data.meta.agrupamento
    }
    if (data.filtros_disponiveis) {
      territorialFiltrosMacrotemas.value = data.filtros_disponiveis.macrotemas
      territorialFiltrosBairros.value = data.filtros_disponiveis.bairros
    }
  }

  async function carregarExecutivo() {
    const data = await apiFetch<ExecutivoApi>('/api/analytics/executivo/')
    mapExecutivo(data)
  }

  async function carregarTerritorial(query: TerritorialQuery = {}) {
    const params = new URLSearchParams()
    const agrup = query.agrupamento ?? territorialAgrupamento.value
    params.set('agrupamento', agrup)
    if (query.macrotemaId != null) {
      params.set('macrotema_id', String(query.macrotemaId))
    }
    if (query.bairro) {
      params.set('bairro', query.bairro)
    }
    const qs = params.toString()
    const data = await apiFetch<TerritorialApi>(`/api/analytics/territorial${qs ? `?${qs}` : ''}`)
    mapTerritorial(data)
  }

  async function carregarDados(opcoes?: {
    executivo?: boolean
    territorial?: boolean
    territorialQuery?: TerritorialQuery
  }) {
    const wantExec = opcoes?.executivo ?? true
    const wantTerr = opcoes?.territorial ?? true
    loading.value = true
    erro.value = null
    try {
      const tasks: Promise<void>[] = []
      if (wantExec) tasks.push(carregarExecutivo())
      if (wantTerr) tasks.push(carregarTerritorial(opcoes?.territorialQuery ?? {}))
      await Promise.all(tasks)
    } catch (e) {
      erro.value = e instanceof Error ? e.message : 'Falha ao carregar analytics'
      produtividade.value = []
      atividadesRecentes.value = []
      gargalos.value = []
      pinsCidadaos.value = []
      zonasCalor.value = []
    } finally {
      loading.value = false
    }
  }

  const topPerformers = computed(() => {
    return [...produtividade.value]
      .sort((a, b) => b.taxaSucesso - a.taxaSucesso)
      .slice(0, 5)
  })

  const worstPerformers = computed(() => {
    return [...produtividade.value]
      .sort((a, b) => a.taxaSucesso - b.taxaSucesso)
      .slice(0, 3)
  })

  const totalAtrasados = computed(() => {
    return produtividade.value.reduce((sum, p) => sum + p.atrasados, 0)
  })

  const totalConcluidos = computed(() => {
    return produtividade.value.reduce((sum, p) => sum + p.concluidos, 0)
  })

  const atividadesRecentes24h = computed(() => {
    const h24 = Date.now() - 24 * 60 * 60 * 1000
    return atividadesRecentes.value.filter(a => new Date(a.timestamp).getTime() > h24)
  })

  return {
    produtividade,
    atividadesRecentes,
    gargalos,
    pinsCidadaos,
    zonasCalor,
    mapaCentro,
    territorialAgrupamento,
    territorialFiltrosMacrotemas,
    territorialFiltrosBairros,
    loading,
    erro,
    topPerformers,
    worstPerformers,
    totalAtrasados,
    totalConcluidos,
    atividadesRecentes24h,
    carregarDados,
    carregarExecutivo,
    carregarTerritorial,
  }
})
