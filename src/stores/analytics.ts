import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiDownload, apiFetch } from '@/services/api'

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

export interface MapBbox {
  swLat: number
  swLng: number
  neLat: number
  neLng: number
}

export interface TerritorialTotais {
  cidadaosGeolocalizados: number
  atendimentosPendentes: number
}

export interface PinsMeta {
  totalGeolocalizados: number
  retornados: number
  limit: number
  limitAplicado: boolean
}

export interface MembroEquipe {
  userId: string
  nome: string
  email: string
  cargo: string
  avatar: string
  totalAtendimentos: number
  taxaSucesso: number
  atrasados?: number
}

export interface AssessorDesempenhoResumo {
  total: number
  concluidos: number
  atrasados: number
  emAndamento: number
  taxaSucesso: number
}

export interface AssessorDesempenhoDetalhe {
  assessor: {
    userId: string
    nome: string
    email: string
    cargo: string
    avatar: string
  }
  periodo: { de: string | null; ate: string | null }
  resumo: AssessorDesempenhoResumo
  porStatus: Array<{ status: string; rotulo: string; quantidade: number }>
  porMacrotema: Array<{ macrotema: string; cor: string; quantidade: number }>
  atendimentosRecentes: Array<{
    id: number
    protocolo: string
    status: string
    statusRotulo: string
    macrotema: string
    cidadaoNome: string
    atrasado: boolean
    updatedAt: string
  }>
  atividades: Array<{ id: string; tipo: string; descricao: string; timestamp: string }>
  comparativoEquipe: {
    taxaSucessoMedia: number
    deltaTaxa: number
    totalEquipe: number
  }
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

interface TerritorialFiltrosApi {
  centro: MapaCentro
  filtros_disponiveis: {
    macrotemas: MacrotemaFiltroOpcao[]
    bairros: string[]
  }
  totais: {
    cidadaos_geolocalizados: number
    atendimentos_pendentes: number
  }
}

interface TerritorialZonasApi {
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
  meta: {
    agrupamento: TerritorialAgrupamento
    macrotema_id: number | null
    bairro: string
  }
}

interface TerritorialPinsApi {
  pins_cidadaos: Array<{
    id: string
    nome: string
    lat: number
    lng: number
    endereco: string
    tags: string[]
  }>
  meta: {
    total_geolocalizados: number
    retornados: number
    limit: number
    limit_aplicado: boolean
  }
}

interface TerritorialApi {
  pins_cidadaos: TerritorialPinsApi['pins_cidadaos']
  zonas_calor: TerritorialZonasApi['zonas_calor']
  centro: MapaCentro
  meta?: TerritorialZonasApi['meta']
  filtros_disponiveis?: TerritorialFiltrosApi['filtros_disponiveis']
  totais?: TerritorialFiltrosApi['totais']
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
  const territorialTotais = ref<TerritorialTotais | null>(null)
  const pinsMeta = ref<PinsMeta | null>(null)
  const loading = ref(false)
  const loadingZonas = ref(false)
  const loadingPins = ref(false)
  const equipeMembros = ref<MembroEquipe[]>([])
  const podeVerEquipe = ref(true)
  const assessorDetalhe = ref<AssessorDesempenhoDetalhe | null>(null)
  const desempenhoLoading = ref(false)
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

  function mapZonasFromApi(zonas: TerritorialZonasApi['zonas_calor']) {
    zonasCalor.value = zonas.map(z => ({
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
  }

  function mapPinsFromApi(pins: TerritorialPinsApi['pins_cidadaos']) {
    pinsCidadaos.value = pins.map(p => ({
      id: p.id,
      nome: p.nome,
      lat: p.lat,
      lng: p.lng,
      endereco: p.endereco,
      tags: p.tags,
    }))
  }

  function mapFiltrosFromApi(data: TerritorialFiltrosApi) {
    mapaCentro.value = data.centro
    territorialFiltrosMacrotemas.value = data.filtros_disponiveis.macrotemas
    territorialFiltrosBairros.value = data.filtros_disponiveis.bairros
    territorialTotais.value = {
      cidadaosGeolocalizados: data.totais.cidadaos_geolocalizados,
      atendimentosPendentes: data.totais.atendimentos_pendentes,
    }
  }

  function mapPinsMetaFromApi(meta: TerritorialPinsApi['meta']) {
    pinsMeta.value = {
      totalGeolocalizados: meta.total_geolocalizados,
      retornados: meta.retornados,
      limit: meta.limit,
      limitAplicado: meta.limit_aplicado,
    }
  }

  function mapTerritorial(data: TerritorialApi) {
    mapPinsFromApi(data.pins_cidadaos)
    mapZonasFromApi(data.zonas_calor)
    mapaCentro.value = data.centro
    if (data.meta?.agrupamento) {
      territorialAgrupamento.value = data.meta.agrupamento
    }
    if (data.filtros_disponiveis && data.totais) {
      mapFiltrosFromApi({
        centro: data.centro,
        filtros_disponiveis: data.filtros_disponiveis,
        totais: data.totais,
      })
    }
  }

  function buildTerritorialSearch(query: TerritorialQuery) {
    const params = new URLSearchParams()
    const agrup = query.agrupamento ?? territorialAgrupamento.value
    params.set('agrupamento', agrup)
    if (query.macrotemaId != null) {
      params.set('macrotema_id', String(query.macrotemaId))
    }
    if (query.bairro) {
      params.set('bairro', query.bairro)
    }
    return params
  }

  async function carregarExecutivo() {
    const data = await apiFetch<ExecutivoApi>('/api/analytics/executivo/')
    mapExecutivo(data)
  }

  async function carregarTerritorialFiltros(query: TerritorialQuery = {}) {
    const params = buildTerritorialSearch(query)
    const data = await apiFetch<TerritorialFiltrosApi>(
      `/api/analytics/territorial/filtros/?${params.toString()}`,
    )
    mapFiltrosFromApi(data)
  }

  async function carregarTerritorialZonas(query: TerritorialQuery = {}) {
    loadingZonas.value = true
    try {
      const params = buildTerritorialSearch(query)
      const data = await apiFetch<TerritorialZonasApi>(
        `/api/analytics/territorial/zonas/?${params.toString()}`,
      )
      mapZonasFromApi(data.zonas_calor)
      if (data.meta?.agrupamento) {
        territorialAgrupamento.value = data.meta.agrupamento
      }
    } finally {
      loadingZonas.value = false
    }
  }

  async function carregarTerritorialPins(
    query: TerritorialQuery & { bbox?: MapBbox | null; limit?: number } = {},
  ) {
    loadingPins.value = true
    try {
      const params = buildTerritorialSearch(query)
      if (query.bbox) {
        params.set('sw_lat', String(query.bbox.swLat))
        params.set('sw_lng', String(query.bbox.swLng))
        params.set('ne_lat', String(query.bbox.neLat))
        params.set('ne_lng', String(query.bbox.neLng))
      }
      if (query.limit != null) {
        params.set('limit', String(query.limit))
      }
      const data = await apiFetch<TerritorialPinsApi>(
        `/api/analytics/territorial/pins/?${params.toString()}`,
      )
      mapPinsFromApi(data.pins_cidadaos)
      mapPinsMetaFromApi(data.meta)
    } finally {
      loadingPins.value = false
    }
  }

  /** Mapa: filtros + zonas (sem baixar todos os pins). */
  async function carregarMapaBase(query: TerritorialQuery = {}) {
    loading.value = true
    erro.value = null
    try {
      await Promise.all([carregarTerritorialFiltros(query), carregarTerritorialZonas(query)])
    } catch (e) {
      erro.value = e instanceof Error ? e.message : 'Falha ao carregar mapa'
      zonasCalor.value = []
      territorialTotais.value = null
      throw e
    } finally {
      loading.value = false
    }
  }

  async function carregarTerritorial(query: TerritorialQuery = {}) {
    const params = buildTerritorialSearch(query)
    const data = await apiFetch<TerritorialApi>(`/api/analytics/territorial/?${params.toString()}`)
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

  async function carregarEquipeDesempenho() {
    const data = await apiFetch<{
      pode_ver_equipe: boolean
      membros: Array<{
        user_id: string
        nome: string
        email: string
        cargo: string
        avatar: string
        total_atendimentos: number
        taxa_sucesso: number
        atrasados?: number
      }>
    }>('/api/analytics/equipe-desempenho/')
    podeVerEquipe.value = data.pode_ver_equipe
    equipeMembros.value = data.membros.map(m => ({
      userId: m.user_id,
      nome: m.nome,
      email: m.email,
      cargo: m.cargo,
      avatar: m.avatar,
      totalAtendimentos: m.total_atendimentos,
      taxaSucesso: m.taxa_sucesso,
      atrasados: m.atrasados,
    }))
    return equipeMembros.value
  }

  async function exportEquipeDesempenhoCsv() {
    return apiDownload('/api/analytics/equipe-desempenho/export/')
  }

  async function exportAssessorDesempenhoCsv(params: {
    responsavelId: string
    de?: string
    ate?: string
  }) {
    const search = new URLSearchParams({ responsavel_id: params.responsavelId })
    if (params.de) search.set('de', params.de)
    if (params.ate) search.set('ate', params.ate)
    return apiDownload(`/api/analytics/assessor-desempenho/export/?${search.toString()}`)
  }

  async function carregarAssessorDesempenho(params: {
    responsavelId: string
    de?: string
    ate?: string
  }) {
    desempenhoLoading.value = true
    erro.value = null
    try {
      const search = new URLSearchParams({ responsavel_id: params.responsavelId })
      if (params.de) search.set('de', params.de)
      if (params.ate) search.set('ate', params.ate)
      const data = await apiFetch<{
        assessor: {
          user_id: string
          nome: string
          email: string
          cargo: string
          avatar: string
        }
        periodo: AssessorDesempenhoDetalhe['periodo']
        resumo: {
          total: number
          concluidos: number
          atrasados: number
          em_andamento: number
          taxa_sucesso: number
        }
        por_status: Array<{ status: string; rotulo: string; quantidade: number }>
        por_macrotema: Array<{ macrotema: string; cor: string; quantidade: number }>
        atendimentos_recentes: Array<{
          id: number
          protocolo: string
          status: string
          status_rotulo: string
          macrotema: string
          cidadao_nome: string
          atrasado: boolean
          updated_at: string
        }>
        atividades: AssessorDesempenhoDetalhe['atividades']
        comparativo_equipe: {
          taxa_sucesso_media: number
          delta_taxa: number
          total_equipe: number
        }
      }>(`/api/analytics/assessor-desempenho/?${search.toString()}`)

      assessorDetalhe.value = {
        assessor: {
          userId: data.assessor.user_id,
          nome: data.assessor.nome,
          email: data.assessor.email,
          cargo: data.assessor.cargo,
          avatar: data.assessor.avatar,
        },
        periodo: data.periodo,
        resumo: {
          total: data.resumo.total,
          concluidos: data.resumo.concluidos,
          atrasados: data.resumo.atrasados,
          emAndamento: data.resumo.em_andamento,
          taxaSucesso: data.resumo.taxa_sucesso,
        },
        porStatus: data.por_status,
        porMacrotema: data.por_macrotema.map(m => ({
          macrotema: m.macrotema,
          cor: m.cor,
          quantidade: m.quantidade,
        })),
        atendimentosRecentes: data.atendimentos_recentes.map(a => ({
          id: a.id,
          protocolo: a.protocolo,
          status: a.status,
          statusRotulo: a.status_rotulo,
          macrotema: a.macrotema,
          cidadaoNome: a.cidadao_nome,
          atrasado: a.atrasado,
          updatedAt: a.updated_at,
        })),
        atividades: data.atividades,
        comparativoEquipe: {
          taxaSucessoMedia: data.comparativo_equipe.taxa_sucesso_media,
          deltaTaxa: data.comparativo_equipe.delta_taxa,
          totalEquipe: data.comparativo_equipe.total_equipe,
        },
      }
      return assessorDetalhe.value
    } catch (e) {
      assessorDetalhe.value = null
      erro.value = e instanceof Error ? e.message : 'Falha ao carregar desempenho'
      throw e
    } finally {
      desempenhoLoading.value = false
    }
  }

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
    territorialTotais,
    pinsMeta,
    loading,
    loadingZonas,
    loadingPins,
    erro,
    topPerformers,
    worstPerformers,
    totalAtrasados,
    totalConcluidos,
    atividadesRecentes24h,
    carregarDados,
    carregarExecutivo,
    carregarTerritorial,
    carregarTerritorialFiltros,
    carregarTerritorialZonas,
    carregarTerritorialPins,
    carregarMapaBase,
    equipeMembros,
    podeVerEquipe,
    assessorDetalhe,
    desempenhoLoading,
    carregarEquipeDesempenho,
    carregarAssessorDesempenho,
    exportEquipeDesempenhoCsv,
    exportAssessorDesempenhoCsv,
  }
})
