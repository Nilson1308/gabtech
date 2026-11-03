import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Atendimento,
  StatusAtendimento,
  Macrotema,
  Despacho,
  Tag,
  TipoTag,
  Usuario,
  Cidadao,
} from '@/types'
import { apiDownload, apiFetch, apiUpload } from '@/services/api'
import { mapRastreabilidade, type RastreabilidadeApi } from '@/utils/rastreabilidade'
import { useCrmStore } from './crm'

export type ExportAtendimentosCsvFiltros = {
  search?: string
  macrotemaIds?: string[]
  tagIds?: string[]
}

export type KanbanFiltros = ExportAtendimentosCsvFiltros

export interface DashboardResumo {
  abertos: number
  slaAtrasados: number
  totalAtendimentos: number
  porMacrotema: Array<{ macrotema: string; quantidade: number; cor: string }>
  recentes: Atendimento[]
  topTags: Array<{ tag: Tag; count: number }>
}

interface DashboardResumoApi {
  abertos: number
  sla_atrasados: number
  total_atendimentos: number
  por_macrotema: Array<{ macrotema: string; quantidade: number; cor: string }>
  recentes: AtendimentoApi[]
  top_tags: Array<{ tag: TagApi; count: number }>
}

const KANBAN_PAGE_SIZE = 25

const STATUS_KANBAN: StatusAtendimento[] = [
  'aberto',
  'em_andamento',
  'aguardando_terceiros',
  'concluido',
]

export interface KanbanColumnState {
  items: Atendimento[]
  page: number
  hasMore: boolean
  total: number
  loadingMore: boolean
}

function criarEstadoColunaKanban(): KanbanColumnState {
  return {
    items: [],
    page: 0,
    hasMore: true,
    total: 0,
    loadingMore: false,
  }
}

function criarKanbanVazio(): Record<StatusAtendimento, KanbanColumnState> {
  return {
    aberto: criarEstadoColunaKanban(),
    em_andamento: criarEstadoColunaKanban(),
    aguardando_terceiros: criarEstadoColunaKanban(),
    concluido: criarEstadoColunaKanban(),
  }
}

function parseOptionalUserId(value: string | undefined | null): number | undefined {
  if (value == null || String(value).trim() === '') return undefined
  const id = Number(value)
  return Number.isFinite(id) && id > 0 ? id : undefined
}

interface DrfPaginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

interface MacrotemaApi {
  id: number
  nome: string
  cor: string
  icone: string
  rastreabilidade?: RastreabilidadeApi
}

interface UsuarioApi {
  id: number
  nome: string
  email: string
  avatar?: string
  cargo: string
  permissions: string[]
}

interface AnexoApi {
  id: number
  nome_original: string
  content_type: string
  tamanho: number
  created_at: string
  url_download?: string | null
}

interface DespachoApi {
  id: number
  autor: UsuarioApi
  autor_id: number
  tipo: Despacho['tipo']
  conteudo: string
  status_anterior?: string
  status_novo?: string
  responsavel_anterior_id?: number | null
  responsavel_novo_id?: number | null
  anexos?: AnexoApi[]
  created_at: string
}

export interface ConfiguracaoSlaApi {
  horas_baixa: number
  horas_media: number
  horas_alta: number
  horas_urgente: number
  dias_baixa?: number
  dias_media?: number
  dias_alta?: number
  dias_urgente?: number
  updated_at: string
}

export type ConfiguracaoSlaUpdatePayload = Partial<
  Pick<
    ConfiguracaoSlaApi,
    | 'horas_baixa'
    | 'horas_media'
    | 'horas_alta'
    | 'horas_urgente'
    | 'dias_baixa'
    | 'dias_media'
    | 'dias_alta'
    | 'dias_urgente'
  >
>

interface TagApi {
  id: number
  nome: string
  cor: string
  tipo?: TipoTag
  modulos?: ('crm' | 'atendimentos')[]
  rastreabilidade?: RastreabilidadeApi
}

function mapTagFromApi(tag: TagApi): Tag {
  const modulos = (tag.modulos?.length ? tag.modulos : ['crm']) as Tag['modulos']
  return {
    id: String(tag.id),
    nome: tag.nome,
    cor: tag.cor,
    tipo: tag.tipo ?? 'ambos',
    modulos,
    rastreabilidade: mapRastreabilidade(tag.rastreabilidade),
  }
}

interface AtendimentoApi {
  id: number
  protocolo: string
  cidadao: {
    id: number
    nome: string
    nome_social?: string
    cpf?: string | null
    telefone: string
    email?: string
    avatar?: string
    bairro?: string
    perfis_profissionais?: Array<{
      id: number
      instituicao: string
      cargo: string
      tag_id: number | null | string
    }>
  }
  perfil_ativo_id?: number | null
  assunto: string
  descricao: string
  macrotema: MacrotemaApi
  tags?: TagApi[]
  status: StatusAtendimento
  responsavel: UsuarioApi
  prioridade: Atendimento['prioridade']
  sla_vencimento: string | null
  sla_horas?: number
  anexos?: AnexoApi[]
  despachos?: DespachoApi[]
  created_at: string
  updated_at: string
  rastreabilidade?: RastreabilidadeApi
}

function mapUsuarioFromApi(u: UsuarioApi): Usuario {
  return {
    id: String(u.id),
    nome: u.nome,
    email: u.email,
    avatar: u.avatar,
    cargo: u.cargo,
    tenantId: '',
    permissions: u.permissions ?? [],
    createdAt: new Date().toISOString(),
  }
}

function mapMacrotemaFromApi(m: MacrotemaApi): Macrotema {
  return {
    id: String(m.id),
    nome: m.nome,
    cor: m.cor,
    icone: m.icone,
    rastreabilidade: mapRastreabilidade(m.rastreabilidade),
  }
}

function mapCidadaoResumoFromApi(c: AtendimentoApi['cidadao']): Cidadao {
  return {
    id: String(c.id),
    nome: c.nome,
    nome_social: c.nome_social,
    cpf: c.cpf ?? undefined,
    telefone: c.telefone,
    email: c.email,
    avatar: c.avatar,
    bairro: c.bairro,
    perfis_profissionais: (c.perfis_profissionais ?? []).map(p => ({
      id: String(p.id),
      instituicao: p.instituicao,
      cargo: p.cargo,
      tag_id: p.tag_id != null ? String(p.tag_id) : '',
    })),
    createdAt: '',
    updatedAt: '',
  }
}

function mapAnexoFromApi(a: AnexoApi): Atendimento['anexos'][number] {
  return {
    id: String(a.id),
    nome: a.nome_original,
    url: a.url_download ?? '',
    tipo: a.content_type,
    tamanho: a.tamanho,
    createdAt: a.created_at,
  }
}

function mapDespachoFromApi(d: DespachoApi, atendimentoId: string): Despacho {
  return {
    id: String(d.id),
    atendimentoId,
    autorId: String(d.autor_id),
    autor: mapUsuarioFromApi(d.autor),
    tipo: d.tipo,
    conteudo: d.conteudo,
    statusAnterior: d.status_anterior as StatusAtendimento | undefined,
    statusNovo: d.status_novo as StatusAtendimento | undefined,
    responsavelAnteriorId: d.responsavel_anterior_id
      ? String(d.responsavel_anterior_id)
      : undefined,
    responsavelNovoId: d.responsavel_novo_id ? String(d.responsavel_novo_id) : undefined,
    anexos: (d.anexos ?? []).map(mapAnexoFromApi),
    createdAt: d.created_at,
  }
}

function slaAtrasado(slaVencimento: string | null, status: StatusAtendimento): boolean {
  if (status === 'concluido' || !slaVencimento) {
    return false
  }
  return new Date() > new Date(slaVencimento)
}

function mapAtendimentoFromApi(item: AtendimentoApi): Atendimento {
  const id = String(item.id)
  return {
    id,
    protocolo: item.protocolo,
    cidadaoId: String(item.cidadao.id),
    cidadao: mapCidadaoResumoFromApi(item.cidadao),
    perfil_ativo_id: item.perfil_ativo_id ? String(item.perfil_ativo_id) : undefined,
    assunto: item.assunto,
    descricao: item.descricao ?? '',
    macrotema: mapMacrotemaFromApi(item.macrotema),
    tags: (item.tags ?? []).map(mapTagFromApi),
    status: item.status,
    responsavelId: String(item.responsavel.id),
    responsavel: mapUsuarioFromApi(item.responsavel),
    prioridade: item.prioridade,
    slaVencimento: item.sla_vencimento ?? '',
    slaHoras: item.sla_horas,
    slaAtrasado: slaAtrasado(item.sla_vencimento, item.status),
    despachos: (item.despachos ?? []).map(d => mapDespachoFromApi(d, id)),
    anexos: (item.anexos ?? []).map(mapAnexoFromApi),
    createdAt: item.created_at,
    updatedAt: item.updated_at,
    rastreabilidade: mapRastreabilidade(item.rastreabilidade),
  }
}

export const useAtendimentosStore = defineStore('atendimentos', () => {
  const atendimentos = ref<Atendimento[]>([])
  const loading = ref(false)
  const macrotemasDisponiveis = ref<Macrotema[]>([])
  const macrotemasLoaded = ref(false)

  const tagsAtendimentoDisponiveis = ref<Tag[]>([])
  const responsaveisElegiveis = ref<Usuario[]>([])

  const kanbanPorStatus = ref<Record<StatusAtendimento, KanbanColumnState>>(criarKanbanVazio())
  const kanbanTotalFiltrado = ref(0)
  const kanbanLoading = ref(false)

  const dashboardResumo = ref<DashboardResumo | null>(null)
  const dashboardLoading = ref(false)

  const atendimentosPorStatus = computed(() => ({
    aberto: atendimentos.value.filter(a => a.status === 'aberto'),
    em_andamento: atendimentos.value.filter(a => a.status === 'em_andamento'),
    aguardando_terceiros: atendimentos.value.filter(a => a.status === 'aguardando_terceiros'),
    concluido: atendimentos.value.filter(a => a.status === 'concluido'),
  }))

  const atendimentosAtrasados = computed(() =>
    atendimentos.value.filter(a => a.slaAtrasado && a.status !== 'concluido'),
  )

  const totalAtendimentos = computed(() => atendimentos.value.length)

  const atendimentosPorMacrotema = computed(() => {
    const grouped = atendimentos.value.reduce(
      (acc, atendimento) => {
        const key = atendimento.macrotema.nome
        if (!acc[key]) {
          acc[key] = { macrotema: key, quantidade: 0, cor: atendimento.macrotema.cor }
        }
        acc[key].quantidade++
        return acc
      },
      {} as Record<string, { macrotema: string; quantidade: number; cor: string }>,
    )
    return Object.values(grouped)
  })

  const topTagsAtendimento = computed(() => {
    const counts = new Map<string, { tag: Tag; count: number }>()

    for (const atendimento of atendimentos.value) {
      for (const tag of atendimento.tags ?? []) {
        const entry = counts.get(tag.id)
        if (entry) {
          entry.count += 1
        } else {
          counts.set(tag.id, { tag, count: 1 })
        }
      }
    }

    return [...counts.values()].sort((a, b) => b.count - a.count).slice(0, 5)
  })

  async function fetchMacrotemas() {
    const data = await apiFetch<MacrotemaApi[] | DrfPaginated<MacrotemaApi>>(
      '/api/atendimentos/macrotemas/',
    )
    const list = Array.isArray(data) ? data : data.results
    macrotemasDisponiveis.value = list.map(mapMacrotemaFromApi)
    macrotemasLoaded.value = true
  }

  async function ensureMacrotemas() {
    if (!macrotemasLoaded.value) {
      await fetchMacrotemas()
    }
  }

  function buildKanbanQueryParams(
    filtros: KanbanFiltros,
    status: StatusAtendimento,
    page: number,
  ): URLSearchParams {
    const params = new URLSearchParams({
      view: 'kanban',
      status,
      page: String(page),
      page_size: String(KANBAN_PAGE_SIZE),
    })
    if (filtros.search?.trim()) {
      params.set('search', filtros.search.trim())
    }
    for (const id of filtros.macrotemaIds ?? []) {
      params.append('macrotema', id)
    }
    for (const id of filtros.tagIds ?? []) {
      params.append('tags', id)
    }
    return params
  }

  function buildKanbanResumoParams(filtros: KanbanFiltros): URLSearchParams {
    const params = new URLSearchParams()
    if (filtros.search?.trim()) {
      params.set('search', filtros.search.trim())
    }
    for (const id of filtros.macrotemaIds ?? []) {
      params.append('macrotema', id)
    }
    for (const id of filtros.tagIds ?? []) {
      params.append('tags', id)
    }
    return params
  }

  function removerDoKanban(id: string) {
    for (const status of STATUS_KANBAN) {
      const col = kanbanPorStatus.value[status]
      const idx = col.items.findIndex(a => a.id === id)
      if (idx >= 0) {
        col.items.splice(idx, 1)
        col.total = Math.max(0, col.total - 1)
        kanbanTotalFiltrado.value = Math.max(0, kanbanTotalFiltrado.value - 1)
        break
      }
    }
  }

  async function fetchKanbanColumnPage(
    status: StatusAtendimento,
    filtros: KanbanFiltros,
    page: number,
    options: { append: boolean },
  ) {
    const { append } = options
    const col = kanbanPorStatus.value[status]
    const params = buildKanbanQueryParams(filtros, status, page)
    const response = await apiFetch<DrfPaginated<AtendimentoApi>>(
      `/api/atendimentos/atendimentos/?${params.toString()}`,
    )
    const mapped = response.results.map(mapAtendimentoFromApi)
    if (append) {
      const existentes = new Set(col.items.map(a => a.id))
      for (const item of mapped) {
        if (!existentes.has(item.id)) {
          col.items.push(item)
        }
      }
    } else {
      col.items = mapped
    }
    col.page = page
    col.total = response.count
    col.hasMore = Boolean(response.next)
  }

  async function fetchKanbanResumo(filtros: KanbanFiltros) {
    const qs = buildKanbanResumoParams(filtros).toString()
    const path = qs
      ? `/api/atendimentos/atendimentos/kanban-resumo/?${qs}`
      : '/api/atendimentos/atendimentos/kanban-resumo/'
    const data = await apiFetch<{
      por_status: Record<StatusAtendimento, number>
      total: number
    }>(path)
    kanbanTotalFiltrado.value = data.total
    for (const status of STATUS_KANBAN) {
      kanbanPorStatus.value[status].total = data.por_status[status] ?? 0
    }
  }

  async function fetchKanban(filtros: KanbanFiltros = {}) {
    kanbanLoading.value = true
    try {
      await Promise.all([ensureMacrotemas(), fetchTagsAtendimento()])
      for (const status of STATUS_KANBAN) {
        Object.assign(kanbanPorStatus.value[status], criarEstadoColunaKanban())
      }
      await fetchKanbanResumo(filtros)
      await Promise.all(
        STATUS_KANBAN.map(status =>
          fetchKanbanColumnPage(status, filtros, 1, { append: false }),
        ),
      )
    } finally {
      kanbanLoading.value = false
    }
  }

  async function loadMoreKanbanColumn(status: StatusAtendimento, filtros: KanbanFiltros) {
    const col = kanbanPorStatus.value[status]
    if (!col.hasMore || col.loadingMore || kanbanLoading.value) {
      return
    }
    col.loadingMore = true
    try {
      await fetchKanbanColumnPage(status, filtros, col.page + 1, { append: true })
    } finally {
      col.loadingMore = false
    }
  }

  async function refreshKanbanColunas(
    statuses: StatusAtendimento[],
    filtros: KanbanFiltros,
  ) {
    await fetchKanbanResumo(filtros)
    await Promise.all(
      statuses.map(status => fetchKanbanColumnPage(status, filtros, 1, { append: false })),
    )
  }

  async function loadAllAtendimentos(): Promise<Atendimento[]> {
    const params = new URLSearchParams({ page_size: '500' })
    const aggregated: Atendimento[] = []
    let page = 1
    let hasNext = true

    while (hasNext) {
      params.set('page', String(page))
      const response = await apiFetch<DrfPaginated<AtendimentoApi>>(
        `/api/atendimentos/atendimentos/?${params.toString()}`,
      )
      aggregated.push(...response.results.map(mapAtendimentoFromApi))
      hasNext = Boolean(response.next)
      page += 1
      if (page > 50) {
        break
      }
    }

    return aggregated
  }

  async function fetchTagsAtendimento() {
    const crmStore = useCrmStore()
    await crmStore.fetchTags()
    tagsAtendimentoDisponiveis.value = crmStore.tagsDisponiveis.filter(tag =>
      tag.modulos.includes('atendimentos'),
    )
  }

  async function ensureTagsAtendimento() {
    if (tagsAtendimentoDisponiveis.value.length === 0) {
      await fetchTagsAtendimento()
    }
  }

  async function fetchAtendimentos() {
    loading.value = true
    try {
      await Promise.all([ensureMacrotemas(), ensureTagsAtendimento()])
      atendimentos.value = await loadAllAtendimentos()
    } finally {
      loading.value = false
    }
  }

  /** Timeline do perfil CRM — só atendimentos do cidadão, paginado (sem carregar o módulo inteiro). */
  async function fetchDashboardResumo(): Promise<DashboardResumo> {
    dashboardLoading.value = true
    try {
      const data = await apiFetch<DashboardResumoApi>(
        '/api/atendimentos/atendimentos/dashboard-resumo/',
      )
      const mapped: DashboardResumo = {
        abertos: data.abertos,
        slaAtrasados: data.sla_atrasados,
        totalAtendimentos: data.total_atendimentos,
        porMacrotema: data.por_macrotema.map(row => ({
          macrotema: row.macrotema,
          quantidade: row.quantidade,
          cor: row.cor,
        })),
        recentes: data.recentes.map(mapAtendimentoFromApi),
        topTags: data.top_tags.map(row => ({
          tag: mapTagFromApi(row.tag),
          count: row.count,
        })),
      }
      dashboardResumo.value = mapped
      return mapped
    } finally {
      dashboardLoading.value = false
    }
  }

  async function fetchAtendimentosPorCidadao(
    cidadaoId: string,
    page = 1,
    pageSize = 25,
  ): Promise<{ items: Atendimento[]; total: number; hasMore: boolean }> {
    const params = new URLSearchParams({
      cidadao_id: cidadaoId,
      page: String(page),
      page_size: String(pageSize),
      view: 'kanban',
    })
    const response = await apiFetch<DrfPaginated<AtendimentoApi>>(
      `/api/atendimentos/atendimentos/?${params.toString()}`,
    )
    return {
      items: response.results.map(mapAtendimentoFromApi),
      total: response.count,
      hasMore: Boolean(response.next),
    }
  }

  async function uploadAnexoAtendimento(
    atendimentoId: string,
    file: File,
    despachoId?: string,
  ): Promise<void> {
    const form = new FormData()
    form.append('atendimento', atendimentoId)
    if (despachoId) {
      form.append('despacho', despachoId)
    }
    form.append('arquivo', file)
    await apiUpload(`/api/atendimentos/anexos/`, form)
  }

  async function downloadAnexoAtendimento(anexo: Atendimento['anexos'][number]): Promise<void> {
    const blob = await apiDownload(`/api/atendimentos/anexos/${anexo.id}/download/`)
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = anexo.nome
    link.click()
    URL.revokeObjectURL(url)
  }

  async function getAtendimentoById(
    id: string,
    options?: { silent?: boolean },
  ): Promise<Atendimento | null> {
    if (!options?.silent) {
      loading.value = true
    }
    try {
      await ensureMacrotemas()
      const data = await apiFetch<AtendimentoApi>(`/api/atendimentos/atendimentos/${id}/`)
      const mapped = mapAtendimentoFromApi(data)
      const index = atendimentos.value.findIndex(a => a.id === id)
      if (index >= 0) {
        atendimentos.value[index] = mapped
      } else {
        atendimentos.value.push(mapped)
      }
      return mapped
    } catch {
      return null
    } finally {
      if (!options?.silent) {
        loading.value = false
      }
    }
  }

  async function createAtendimento(
    data: Partial<Atendimento>,
    arquivos?: File[],
  ): Promise<Atendimento> {
    loading.value = true
    try {
      const payload = {
        cidadao_id: Number(data.cidadaoId),
        macrotema_id: Number(data.macrotema?.id ?? data.macrotema),
        assunto: data.assunto,
        descricao: data.descricao,
        prioridade: data.prioridade ?? 'media',
        responsavel_id: parseOptionalUserId(data.responsavelId),
        perfil_ativo_id: data.perfil_ativo_id ? Number(data.perfil_ativo_id) : null,
        tag_ids: (data.tags ?? []).map(t => Number(t.id)),
      }

      const created = await apiFetch<AtendimentoApi>('/api/atendimentos/atendimentos/', {
        method: 'POST',
        body: JSON.stringify(payload),
      })
      const id = String(created.id)
      let mapped = mapAtendimentoFromApi(created)
      for (const file of arquivos ?? []) {
        await uploadAnexoAtendimento(id, file)
      }
      if (arquivos?.length) {
        mapped = (await getAtendimentoById(id, { silent: true })) ?? mapped
      }
      const existing = atendimentos.value.findIndex(a => a.id === id)
      if (existing >= 0) {
        atendimentos.value[existing] = mapped
      } else {
        atendimentos.value.unshift(mapped)
      }
      return mapped
    } finally {
      loading.value = false
    }
  }

  async function updateAtendimento(
    id: string,
    data: Partial<Atendimento>,
    arquivos?: File[],
  ): Promise<Atendimento | null> {
    loading.value = true
    try {
      const payload: Record<string, unknown> = {
        cidadao_id: Number(data.cidadaoId),
        macrotema_id: Number(data.macrotema?.id ?? data.macrotema),
        assunto: data.assunto,
        descricao: data.descricao,
        prioridade: data.prioridade,
        perfil_ativo_id: data.perfil_ativo_id ? Number(data.perfil_ativo_id) : null,
        tag_ids: (data.tags ?? []).map(t => Number(t.id)),
      }
      const responsavelId = parseOptionalUserId(data.responsavelId)
      if (responsavelId !== undefined) {
        payload.responsavel_id = responsavelId
      }
      const mapped = await patchAtendimento(id, payload)
      if (!mapped) {
        return null
      }
      for (const file of arquivos ?? []) {
        await uploadAnexoAtendimento(id, file)
      }
      if (arquivos?.length) {
        return await getAtendimentoById(id, { silent: true })
      }
      return mapped
    } finally {
      loading.value = false
    }
  }

  async function patchAtendimento(
    id: string,
    payload: Record<string, unknown>,
  ): Promise<Atendimento | null> {
    const updated = await apiFetch<AtendimentoApi>(`/api/atendimentos/atendimentos/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    })
    const mapped = mapAtendimentoFromApi(updated)
    const index = atendimentos.value.findIndex(a => a.id === id)
    if (index >= 0) {
      atendimentos.value[index] = mapped
    }
    return mapped
  }

  async function updateStatus(
    id: string,
    novoStatus: StatusAtendimento,
    options?: { silent?: boolean },
  ): Promise<boolean> {
    if (!options?.silent) {
      loading.value = true
    }
    try {
      await patchAtendimento(id, { status: novoStatus })
      return true
    } catch {
      return false
    } finally {
      if (!options?.silent) {
        loading.value = false
      }
    }
  }

  async function addDespacho(
    atendimentoId: string,
    conteudo: string,
    tipo: 'nota_interna' | 'nota_publica' = 'nota_interna',
    arquivos?: File[],
  ): Promise<Atendimento | null> {
    try {
      const despacho = await apiFetch<DespachoApi>('/api/atendimentos/despachos/', {
        method: 'POST',
        body: JSON.stringify({
          atendimento_id: Number(atendimentoId),
          tipo,
          conteudo,
        }),
      })
      const despachoId = String(despacho.id)
      for (const file of arquivos ?? []) {
        await uploadAnexoAtendimento(atendimentoId, file, despachoId)
      }
      return await getAtendimentoById(atendimentoId, { silent: true })
    } catch {
      return null
    }
  }

  async function deleteAtendimento(id: string): Promise<boolean> {
    loading.value = true
    try {
      await apiFetch(`/api/atendimentos/atendimentos/${id}/`, {
        method: 'DELETE',
        parseJson: false,
      })
      const index = atendimentos.value.findIndex(a => a.id === id)
      if (index > -1) {
        atendimentos.value.splice(index, 1)
      }
      removerDoKanban(id)
      return true
    } catch {
      return false
    } finally {
      loading.value = false
    }
  }

  async function reatribuirResponsavel(
    atendimentoId: string,
    novoResponsavelId: string,
  ): Promise<boolean> {
    const responsavelId = parseOptionalUserId(novoResponsavelId)
    if (responsavelId === undefined) {
      return false
    }
    loading.value = true
    try {
      await patchAtendimento(atendimentoId, { responsavel_id: responsavelId })
      return true
    } catch {
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchResponsaveisElegiveis() {
    const data = await apiFetch<UsuarioApi[]>('/api/atendimentos/responsaveis/')
    responsaveisElegiveis.value = data.map(mapUsuarioFromApi)
    return responsaveisElegiveis.value
  }

  async function createMacrotema(data: { nome: string; cor: string; icone: string }) {
    const created = await apiFetch<MacrotemaApi>('/api/atendimentos/macrotemas/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
    const mapped = mapMacrotemaFromApi(created)
    macrotemasDisponiveis.value.push(mapped)
    return mapped
  }

  async function updateMacrotema(id: string, data: { nome: string; cor: string; icone: string }) {
    const updated = await apiFetch<MacrotemaApi>(`/api/atendimentos/macrotemas/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
    const mapped = mapMacrotemaFromApi(updated)
    const index = macrotemasDisponiveis.value.findIndex(m => m.id === id)
    if (index >= 0) {
      macrotemasDisponiveis.value[index] = mapped
    }
    return mapped
  }

  async function deleteMacrotema(id: string) {
    await apiFetch(`/api/atendimentos/macrotemas/${id}/`, {
      method: 'DELETE',
      parseJson: false,
    })
    macrotemasDisponiveis.value = macrotemasDisponiveis.value.filter(m => m.id !== id)
  }

  async function createTagAtendimento(data: { nome: string; cor: string }): Promise<Tag> {
    const crmStore = useCrmStore()
    const tag = await crmStore.createTag({
      nome: data.nome,
      cor: data.cor,
      modulos: ['atendimentos'],
      tipo: 'segmentacao',
    })
    if (tag.modulos.includes('atendimentos')
      && !tagsAtendimentoDisponiveis.value.some(t => t.id === tag.id)) {
      tagsAtendimentoDisponiveis.value.push(tag)
    }
    return tag
  }

  async function updateTagAtendimento(id: string, data: { nome: string; cor: string }) {
    const crmStore = useCrmStore()
    return crmStore.updateTag(id, { ...data, modulos: ['atendimentos'], tipo: 'segmentacao' })
  }

  async function fetchConfiguracaoSla(): Promise<ConfiguracaoSlaApi> {
    return apiFetch<ConfiguracaoSlaApi>('/api/atendimentos/configuracao-sla/')
  }

  async function updateConfiguracaoSla(payload: ConfiguracaoSlaUpdatePayload): Promise<ConfiguracaoSlaApi> {
    return apiFetch<ConfiguracaoSlaApi>('/api/atendimentos/configuracao-sla/', {
      method: 'PATCH',
      body: JSON.stringify(payload),
    })
  }

  async function deleteTagAtendimento(id: string) {
    const crmStore = useCrmStore()
    const ok = await crmStore.deleteTag(id)
    if (ok) {
      tagsAtendimentoDisponiveis.value = tagsAtendimentoDisponiveis.value.filter(t => t.id !== id)
    }
    return ok
  }

  async function exportAtendimentosCsv(filtros: ExportAtendimentosCsvFiltros = {}) {
    const params = new URLSearchParams()
    if (filtros.search?.trim()) {
      params.set('search', filtros.search.trim())
    }
    for (const id of filtros.macrotemaIds ?? []) {
      params.append('macrotema', id)
    }
    for (const id of filtros.tagIds ?? []) {
      params.append('tag', id)
    }
    const qs = params.toString()
    const path = qs
      ? `/api/atendimentos/atendimentos/exportar-csv/?${qs}`
      : '/api/atendimentos/atendimentos/exportar-csv/'
    return apiDownload(path)
  }

  return {
    atendimentos,
    loading,
    macrotemasDisponiveis,
    tagsAtendimentoDisponiveis,
    responsaveisElegiveis,
    fetchResponsaveisElegiveis,
    atendimentosPorStatus,
    atendimentosAtrasados,
    totalAtendimentos,
    atendimentosPorMacrotema,
    topTagsAtendimento,
    fetchMacrotemas,
    fetchTagsAtendimento,
    fetchAtendimentos,
    fetchDashboardResumo,
    dashboardResumo,
    dashboardLoading,
    fetchAtendimentosPorCidadao,
    kanbanPorStatus,
    kanbanTotalFiltrado,
    kanbanLoading,
    fetchKanban,
    loadMoreKanbanColumn,
    refreshKanbanColunas,
    getAtendimentoById,
    createAtendimento,
    updateAtendimento,
    updateStatus,
    addDespacho,
    uploadAnexoAtendimento,
    downloadAnexoAtendimento,
    deleteAtendimento,
    exportAtendimentosCsv,
    reatribuirResponsavel,
    createMacrotema,
    updateMacrotema,
    deleteMacrotema,
    createTagAtendimento,
    updateTagAtendimento,
    deleteTagAtendimento,
    fetchConfiguracaoSla,
    updateConfiguracaoSla,
  }
})
