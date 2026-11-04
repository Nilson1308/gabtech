import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ApiError, apiFetch } from '@/services/api'
import { mapRastreabilidade, type RastreabilidadeApi } from '@/utils/rastreabilidade'
import {
  DEFAULT_CREDENCIAMENTO_CONFIG,
  normalizeCredenciamentoConfig,
  type CredenciamentoConfig,
} from '@/constants/credenciamento'

export type { CredenciamentoConfig }

export interface ItemChecklist {
  id: string
  categoria: 'infraestrutura' | 'buffet' | 'cerimonial' | 'comunicacao' | 'seguranca' | 'tecnologia'
  descricao: string
  status: 'pendente' | 'providenciado' | 'cancelado'
  responsavel?: string
  prazo?: string
  observacoes?: string
  createdAt: string
  updatedAt?: string
}

export interface ItemChecklistPadrao {
  id: string
  categoria: ItemChecklist['categoria']
  descricao: string
  createdAt: string
}

export interface ConvidadoCidadaoResumo {
  id: string
  nome: string
  avatar?: string
  email?: string
  telefone?: string
}

export interface ConvidadoPerfilResumo {
  id: string
  cargo: string
  instituicao: string
}

export interface Convidado {
  id: string
  cidadaoId: string
  perfil_ativo_id?: string
  eventoId: string
  statusConfirmacao: 'pendente' | 'confirmado' | 'recusado'
  ordemPrecedencia: number
  isVip: boolean
  observacoes?: string
  createdAt: string
  updatedAt?: string
  cidadao?: ConvidadoCidadaoResumo
  perfilAtivo?: ConvidadoPerfilResumo
}

export interface Credenciado {
  id: string
  eventoId: string
  nome: string
  telefone: string
  email?: string
  data_nascimento?: string | null
  orgao_instituicao?: string
  cpf?: string
  aceitou_lgpd: boolean
  data_registro: string
  status_presenca: 'pendente' | 'presente'
}

export interface ComunicacaoDisparo {
  id: string
  eventoId: string
  canal: 'email' | 'whatsapp' | 'sms'
  publicoAlvo: {
    convidados: boolean
    tagsCrm: string[]
    quantidade_estimada?: number
  }
  mensagem: string
  quantidadeEnvios: number
  status: 'processando' | 'enviado' | 'falha'
  dataHora: string
}

export interface Evento {
  id: string
  titulo: string
  tipo: 'cerimonial' | 'audiencia' | 'sessao' | 'reuniao'
  data: string
  horaInicio: string
  horaFim: string
  local: string
  descricao?: string
  totalConvidados: number
  status: 'planejamento' | 'confirmado' | 'em_andamento' | 'concluido' | 'cancelado'
  checklist: ItemChecklist[]
  convidados: Convidado[]
  credenciados: Credenciado[]
  comunicacoes: ComunicacaoDisparo[]
  createdAt: string
  tokenLogistica?: string | null
  logisticaPublicaAtiva?: boolean
  observacaoLogisticaExterna?: string
  credenciamentoConfig: CredenciamentoConfig
  rastreabilidade?: import('@/utils/rastreabilidade').Rastreabilidade | null
}

interface AgendaApi {
  id: number
  titulo: string
  descricao?: string
  data: string
  hora_inicio: string
  hora_fim: string
  local: string
  tipo_nome?: string
  status: string
}

interface EventoCerimonialApi {
  id: number
  status_logistico: string
  token_logistica?: string | null
  logistica_publica_ativa?: boolean
  observacao_logistica_externa?: string
  credenciamento_config?: Partial<CredenciamentoConfig>
  created_at: string
  updated_at?: string
  agenda?: AgendaApi
  checklist?: ItemChecklistApi[]
  convidados?: ConvidadoApi[]
  credenciados?: CredenciadoApi[]
  comunicacoes?: ComunicacaoApi[]
  total_convidados?: number
  rastreabilidade?: RastreabilidadeApi
}

interface ItemChecklistApi {
  id: number
  categoria: string
  descricao: string
  status: string
  responsavel?: string
  prazo?: string | null
  observacoes?: string
  created_at: string
  updated_at: string
}

interface ConvidadoApi {
  id: number
  cidadao: { id: number; nome: string; avatar?: string; email?: string; telefone?: string }
  perfil_ativo?: { id: number; cargo: string; instituicao: string } | null
  status_confirmacao: string
  ordem_precedencia: number
  is_vip: boolean
  observacoes?: string
  created_at: string
  updated_at: string
}

interface CredenciadoApi {
  id: number
  nome: string
  telefone: string
  email?: string
  data_nascimento?: string | null
  orgao_instituicao?: string
  cpf?: string
  aceitou_lgpd: boolean
  data_registro: string
  status_presenca: string
}

interface ComunicacaoApi {
  id: number
  canal: string
  mensagem: string
  publico_alvo: Record<string, unknown>
  quantidade_envios: number
  status: string
  data_hora: string
}

interface DrfPaginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface EventosResumo {
  total: number
  confirmados: number
  porStatus: {
    planejamento: number
    executando: number
    concluido: number
    cancelado: number
  }
}

interface EventosResumoApi {
  total: number
  confirmados: number
  por_status: {
    planejamento: number
    executando: number
    concluido: number
    cancelado: number
  }
}

function mapResumoFromApi(data: EventosResumoApi): EventosResumo {
  return {
    total: data.total,
    confirmados: data.confirmados,
    porStatus: {
      planejamento: data.por_status.planejamento,
      executando: data.por_status.executando,
      concluido: data.por_status.concluido,
      cancelado: data.por_status.cancelado,
    },
  }
}

function mapStatusFiltroToApi(status: string): string | undefined {
  if (status === 'todos') return undefined
  const map: Record<string, string> = {
    planejamento: 'planejamento',
    em_andamento: 'executando',
    concluido: 'concluido',
    cancelado: 'cancelado',
    confirmado: 'confirmado',
  }
  return map[status]
}

function mapStatusFromApi(status: string): Evento['status'] {
  const map: Record<string, Evento['status']> = {
    planejamento: 'planejamento',
    executando: 'em_andamento',
    concluido: 'concluido',
    cancelado: 'cancelado',
    confirmado: 'confirmado',
  }
  return map[status] ?? 'planejamento'
}

function mapStatusToApi(status: Evento['status']): string {
  const map: Record<Evento['status'], string> = {
    planejamento: 'planejamento',
    em_andamento: 'executando',
    concluido: 'concluido',
    cancelado: 'cancelado',
    confirmado: 'planejamento',
  }
  return map[status] ?? 'planejamento'
}

function mapChecklist(item: ItemChecklistApi): ItemChecklist {
  return {
    id: String(item.id),
    categoria: item.categoria as ItemChecklist['categoria'],
    descricao: item.descricao,
    status: item.status as ItemChecklist['status'],
    responsavel: item.responsavel || undefined,
    prazo: item.prazo || undefined,
    observacoes: item.observacoes || undefined,
    createdAt: item.created_at,
    updatedAt: item.updated_at,
  }
}

function mapConvidado(item: ConvidadoApi, eventoId: string): Convidado {
  return {
    id: String(item.id),
    cidadaoId: String(item.cidadao.id),
    perfil_ativo_id: item.perfil_ativo ? String(item.perfil_ativo.id) : undefined,
    eventoId,
    statusConfirmacao: item.status_confirmacao as Convidado['statusConfirmacao'],
    ordemPrecedencia: item.ordem_precedencia,
    isVip: item.is_vip,
    observacoes: item.observacoes,
    createdAt: item.created_at,
    updatedAt: item.updated_at,
    cidadao: {
      id: String(item.cidadao.id),
      nome: item.cidadao.nome,
      avatar: item.cidadao.avatar,
      email: item.cidadao.email,
      telefone: item.cidadao.telefone,
    },
    perfilAtivo: item.perfil_ativo
      ? {
          id: String(item.perfil_ativo.id),
          cargo: item.perfil_ativo.cargo,
          instituicao: item.perfil_ativo.instituicao,
        }
      : undefined,
  }
}

function mapCredenciado(item: CredenciadoApi, eventoId: string): Credenciado {
  return {
    id: String(item.id),
    eventoId,
    nome: item.nome,
    telefone: item.telefone,
    email: item.email || undefined,
    data_nascimento: item.data_nascimento ?? undefined,
    orgao_instituicao: item.orgao_instituicao || undefined,
    cpf: item.cpf || undefined,
    aceitou_lgpd: item.aceitou_lgpd,
    data_registro: item.data_registro,
    status_presenca: item.status_presenca as Credenciado['status_presenca'],
  }
}

function mapComunicacao(item: ComunicacaoApi, eventoId: string): ComunicacaoDisparo {
  const publico = item.publico_alvo || {}
  return {
    id: String(item.id),
    eventoId,
    canal: item.canal as ComunicacaoDisparo['canal'],
    publicoAlvo: {
      convidados: Boolean(publico.convidados),
      tagsCrm: (publico.tagsCrm as string[]) || (publico.tags_crm as string[]) || [],
      quantidade_estimada: publico.quantidade_estimada as number | undefined,
    },
    mensagem: item.mensagem,
    quantidadeEnvios: item.quantidade_envios,
    status: item.status as ComunicacaoDisparo['status'],
    dataHora: item.data_hora,
  }
}

function mapEventoFromApi(item: EventoCerimonialApi, full = false): Evento {
  const eventoId = String(item.id)
  const agenda = item.agenda
  return {
    id: eventoId,
    titulo: agenda?.titulo ?? '',
    tipo: 'cerimonial',
    data: agenda?.data ?? '',
    horaInicio: agenda?.hora_inicio ?? '',
    horaFim: agenda?.hora_fim ?? '',
    local: agenda?.local ?? '',
    descricao: agenda?.descricao,
    totalConvidados: item.total_convidados ?? item.convidados?.length ?? 0,
    status: mapStatusFromApi(item.status_logistico),
    createdAt: item.created_at,
    tokenLogistica: item.token_logistica ?? null,
    logisticaPublicaAtiva: Boolean(item.logistica_publica_ativa),
    observacaoLogisticaExterna: item.observacao_logistica_externa || '',
    credenciamentoConfig: normalizeCredenciamentoConfig(item.credenciamento_config),
    checklist: full ? (item.checklist ?? []).map(mapChecklist) : [],
    convidados: full ? (item.convidados ?? []).map(c => mapConvidado(c, eventoId)) : [],
    credenciados: full ? (item.credenciados ?? []).map(c => mapCredenciado(c, eventoId)) : [],
    comunicacoes: full ? (item.comunicacoes ?? []).map(c => mapComunicacao(c, eventoId)) : [],
    rastreabilidade: mapRastreabilidade(item.rastreabilidade),
  }
}

export const useCerimonialStore = defineStore('cerimonial', () => {
  const eventos = ref<Evento[]>([])

  function upsertEvento(mapped: Evento, replaceNested = false) {
    const index = eventos.value.findIndex(e => e.id === mapped.id)
    if (index >= 0) {
      const prev = eventos.value[index]
      eventos.value[index] = replaceNested
        ? mapped
        : {
            ...prev,
            ...mapped,
            checklist: mapped.checklist.length ? mapped.checklist : prev.checklist,
            convidados: mapped.convidados.length ? mapped.convidados : prev.convidados,
            credenciados: mapped.credenciados.length ? mapped.credenciados : prev.credenciados,
            comunicacoes: mapped.comunicacoes.length ? mapped.comunicacoes : prev.comunicacoes,
          }
    } else {
      eventos.value.push(mapped)
    }
  }
  const itensPadrao = ref<ItemChecklistPadrao[]>([])
  const loading = ref(false)
  const listLoading = ref(false)
  const eventoPublico = ref<Partial<Evento> | null>(null)
  const resumo = ref<EventosResumo | null>(null)
  const listTotal = ref(0)
  const listPage = ref(1)
  const listPageSize = ref(30)
  const listFiltroStatus = ref<string>('todos')
  const listBusca = ref('')

  const eventosListagem = computed(() => eventos.value)

  function buildListQuery(page: number) {
    const search = new URLSearchParams({
      page: String(page),
      page_size: String(listPageSize.value),
    })
    const q = listBusca.value.trim()
    if (q) search.set('q', q)
    const statusApi = mapStatusFiltroToApi(listFiltroStatus.value)
    if (statusApi) search.set('status_logistico', statusApi)
    return search.toString()
  }

  async function fetchResumo() {
    const data = await apiFetch<EventosResumoApi>('/api/cerimonial/eventos/resumo/')
    resumo.value = mapResumoFromApi(data)
    return resumo.value
  }

  async function fetchEventosPagina(page = 1) {
    listLoading.value = true
    try {
      const data = await apiFetch<DrfPaginated<EventoCerimonialApi>>(
        `/api/cerimonial/eventos/?${buildListQuery(page)}`,
      )
      eventos.value = data.results.map(item => mapEventoFromApi(item, false))
      listTotal.value = data.count
      listPage.value = page
      return eventos.value
    } finally {
      listLoading.value = false
    }
  }

  async function setListFiltros(filtros: { q?: string; status?: string }) {
    if (filtros.q !== undefined) listBusca.value = filtros.q
    if (filtros.status !== undefined) listFiltroStatus.value = filtros.status
    await fetchEventosPagina(1)
  }

  async function recarregarListagem() {
    await Promise.all([fetchResumo(), fetchEventosPagina(listPage.value)])
  }

  /** @deprecated Use fetchEventosPagina */
  async function fetchEventos() {
    return fetchEventosPagina(1)
  }

  async function fetchChecklistPadrao() {
    const data = await apiFetch<{ id: number; categoria: string; descricao: string; created_at: string }[]>(
      '/api/cerimonial/checklist-padrao/',
    )
    itensPadrao.value = data.map(item => ({
      id: String(item.id),
      categoria: item.categoria as ItemChecklistPadrao['categoria'],
      descricao: item.descricao,
      createdAt: item.created_at,
    }))
  }

  async function initialize() {
    loading.value = true
    try {
      await Promise.all([fetchChecklistPadrao(), fetchResumo(), fetchEventosPagina(1)])
    } finally {
      loading.value = false
    }
  }

  async function fetchEventoDashboard(id: string) {
    loading.value = true
    try {
      const data = await apiFetch<EventoCerimonialApi>(`/api/cerimonial/eventos/${id}/`)
      const mapped = mapEventoFromApi(data, true)
      upsertEvento(mapped, true)
      return mapped
    } finally {
      loading.value = false
    }
  }

  async function fetchEventoPublico(id: string) {
    const data = await apiFetch<{
      id: number
      titulo: string
      data: string
      hora_inicio: string
      hora_fim: string
      local: string
      status_logistico: string
      credenciamento_config?: Partial<CredenciamentoConfig>
    }>(`/api/cerimonial/eventos/${id}/publico/`, { skipAuth: true })
    eventoPublico.value = {
      id: String(data.id),
      titulo: data.titulo,
      data: data.data,
      horaInicio: data.hora_inicio,
      horaFim: data.hora_fim,
      local: data.local,
      status: mapStatusFromApi(data.status_logistico),
      credenciamentoConfig: normalizeCredenciamentoConfig(data.credenciamento_config),
    } as Evento
    return eventoPublico.value
  }

  async function atualizarCredenciamentoConfig(eventoId: string, config: CredenciamentoConfig) {
    const data = await apiFetch<EventoCerimonialApi>(`/api/cerimonial/eventos/${eventoId}/`, {
      method: 'PATCH',
      body: JSON.stringify({ credenciamento_config: config }),
    })
    const mapped = mapEventoFromApi(data, true)
    upsertEvento(mapped, true)
    return mapped.credenciamentoConfig
  }

  function getEventoById(id: string) {
    return eventos.value.find(e => e.id === id)
  }

  async function toggleItemChecklist(eventoId: string, itemId: string) {
    const updated = await apiFetch<ItemChecklistApi>(
      `/api/cerimonial/checklist-itens/${itemId}/toggle/`,
      { method: 'POST' },
    )
    const evento = getEventoById(eventoId)
    if (evento) {
      const idx = evento.checklist.findIndex(i => i.id === itemId)
      const mapped = mapChecklist(updated)
      if (idx >= 0) evento.checklist[idx] = mapped
      else evento.checklist.push(mapped)
    }
  }

  async function adicionarItemChecklist(
    eventoId: string,
    item: Omit<ItemChecklist, 'id' | 'createdAt'>,
  ) {
    const created = await apiFetch<ItemChecklistApi>('/api/cerimonial/checklist-itens/', {
      method: 'POST',
      body: JSON.stringify({
        evento_id: Number(eventoId),
        categoria: item.categoria,
        descricao: item.descricao,
        status: item.status || 'pendente',
        responsavel: item.responsavel || '',
        prazo: item.prazo || null,
        observacoes: item.observacoes || '',
      }),
    })
    const evento = getEventoById(eventoId)
    const mapped = mapChecklist(created)
    evento?.checklist.push(mapped)
    return mapped
  }

  async function removerItemChecklist(eventoId: string, itemId: string) {
    await apiFetch(`/api/cerimonial/checklist-itens/${itemId}/`, {
      method: 'DELETE',
      parseJson: false,
    })
    const evento = getEventoById(eventoId)
    if (evento) {
      evento.checklist = evento.checklist.filter(i => i.id !== itemId)
    }
  }

  const checklistPorCategoria = computed(() => (eventoId: string) => {
    const evento = eventos.value.find(e => e.id === eventoId)
    if (!evento) return {}
    const categorias: Record<string, ItemChecklist[]> = {
      infraestrutura: [],
      buffet: [],
      cerimonial: [],
      comunicacao: [],
      seguranca: [],
      tecnologia: [],
    }
    evento.checklist.forEach(item => {
      categorias[item.categoria]?.push(item)
    })
    return categorias
  })

  const progressoChecklist = computed(() => (eventoId: string) => {
    const evento = eventos.value.find(e => e.id === eventoId)
    if (!evento) return { total: 0, providenciados: 0, percentual: 0 }
    const total = evento.checklist.length
    const providenciados = evento.checklist.filter(i => i.status === 'providenciado').length
    return { total, providenciados, percentual: total > 0 ? Math.round((providenciados / total) * 100) : 0 }
  })

  function parseApiId(value: string, label: string): number {
    const id = Number(String(value).trim())
    if (!Number.isFinite(id) || id <= 0) {
      throw new ApiError(`${label} inválido.`, 400)
    }
    return id
  }

  async function adicionarConvidado(eventoId: string, cidadaoId: string, perfilAtivoId?: string) {
    const payload: Record<string, number> = {
      evento_id: parseApiId(eventoId, 'Evento'),
      cidadao_id: parseApiId(cidadaoId, 'Cidadão'),
    }
    const perfilRaw = perfilAtivoId?.trim()
    if (perfilRaw) {
      payload.perfil_ativo_id = parseApiId(perfilRaw, 'Perfil profissional')
    }

    const created = await apiFetch<ConvidadoApi>('/api/cerimonial/convidados/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    const mapped = mapConvidado(created, eventoId)
    const evento = getEventoById(eventoId)
    evento?.convidados.push(mapped)
    if (evento) evento.totalConvidados = evento.convidados.length
    return mapped
  }

  async function atualizarConvidado(eventoId: string, convidadoId: string, dados: Partial<Convidado>) {
    const payload: Record<string, unknown> = {}
    if (dados.statusConfirmacao) payload.status_confirmacao = dados.statusConfirmacao
    if (dados.isVip !== undefined) payload.is_vip = dados.isVip
    if (dados.perfil_ativo_id !== undefined) {
      payload.perfil_ativo_id = dados.perfil_ativo_id ? Number(dados.perfil_ativo_id) : null
    }
    if (dados.observacoes !== undefined) payload.observacoes = dados.observacoes
    if (dados.ordemPrecedencia !== undefined) payload.ordem_precedencia = dados.ordemPrecedencia

    const updated = await apiFetch<ConvidadoApi>(`/api/cerimonial/convidados/${convidadoId}/`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    })
    const mapped = mapConvidado(updated, eventoId)
    const evento = getEventoById(eventoId)
    const idx = evento?.convidados.findIndex(c => c.id === convidadoId) ?? -1
    if (evento && idx >= 0) evento.convidados[idx] = mapped
    return mapped
  }

  async function removerConvidado(eventoId: string, convidadoId: string) {
    await apiFetch(`/api/cerimonial/convidados/${convidadoId}/`, {
      method: 'DELETE',
      parseJson: false,
    })
    const evento = getEventoById(eventoId)
    if (evento) {
      evento.convidados = evento.convidados.filter(c => c.id !== convidadoId)
      evento.totalConvidados = evento.convidados.length
    }
  }

  async function atualizarOrdemPrecedencia(eventoId: string, convidadoId: string, novaOrdem: number) {
    await atualizarConvidado(eventoId, convidadoId, { ordemPrecedencia: novaOrdem })
  }

  async function salvarOrdemConvidados(eventoId: string, convidadosOrdenados: Convidado[]) {
    const data = await apiFetch<ConvidadoApi[]>(
      `/api/cerimonial/eventos/${eventoId}/reordenar-convidados/`,
      {
        method: 'POST',
        body: JSON.stringify({
          ordens: convidadosOrdenados.map((c, index) => ({
            id: Number(c.id),
            ordem_precedencia: index + 1,
          })),
        }),
      },
    )
    const evento = getEventoById(eventoId)
    if (evento) {
      evento.convidados = data.map(c => mapConvidado(c, eventoId))
    }
  }

  const convidadosOrdenados = computed(() => (eventoId: string) => {
    const evento = eventos.value.find(e => e.id === eventoId)
    if (!evento) return []
    return [...evento.convidados].sort((a, b) => a.ordemPrecedencia - b.ordemPrecedencia)
  })

  const convidadosConfirmados = computed(() => (eventoId: string) => {
    const evento = eventos.value.find(e => e.id === eventoId)
    if (!evento) return []
    return evento.convidados.filter(c => c.statusConfirmacao === 'confirmado')
  })

  async function adicionarItemPadrao(dados: Omit<ItemChecklistPadrao, 'id' | 'createdAt'>) {
    const created = await apiFetch<{ id: number; categoria: string; descricao: string; created_at: string }>(
      '/api/cerimonial/checklist-padrao/',
      {
        method: 'POST',
        body: JSON.stringify(dados),
      },
    )
    const mapped = {
      id: String(created.id),
      categoria: created.categoria as ItemChecklistPadrao['categoria'],
      descricao: created.descricao,
      createdAt: created.created_at,
    }
    itensPadrao.value.push(mapped)
    return mapped
  }

  async function removerItemPadrao(itemId: string) {
    await apiFetch(`/api/cerimonial/checklist-padrao/${itemId}/`, {
      method: 'DELETE',
      parseJson: false,
    })
    itensPadrao.value = itensPadrao.value.filter(i => i.id !== itemId)
  }

  async function adicionarItemPadraoAoEvento(
    eventoId: string,
    itemPadraoId: string,
    responsavel?: string,
    prazo?: string,
  ) {
    const padrao = itensPadrao.value.find(i => i.id === itemPadraoId)
    if (!padrao) return
    return adicionarItemChecklist(eventoId, {
      categoria: padrao.categoria,
      descricao: padrao.descricao,
      status: 'pendente',
      responsavel,
      prazo,
    })
  }

  const itensPadraoPorCategoria = computed(() => {
    const categorias: Record<string, ItemChecklistPadrao[]> = {
      infraestrutura: [],
      buffet: [],
      cerimonial: [],
      comunicacao: [],
      seguranca: [],
      tecnologia: [],
    }
    itensPadrao.value.forEach(item => {
      categorias[item.categoria]?.push(item)
    })
    return categorias
  })

  async function registrarCredenciamento(
    eventoId: string,
    dados: Omit<Credenciado, 'id' | 'eventoId' | 'data_registro' | 'status_presenca'>,
    options?: { publico?: boolean },
  ) {
    const path = options?.publico
      ? `/api/cerimonial/eventos/${eventoId}/credenciamento-publico/`
      : '/api/cerimonial/credenciados/'

    const created = await apiFetch<CredenciadoApi>(path, {
      method: 'POST',
      skipAuth: options?.publico,
      body: JSON.stringify({
        evento_id: Number(eventoId),
        nome: dados.nome,
        telefone: dados.telefone,
        email: dados.email || '',
        data_nascimento: dados.data_nascimento || null,
        orgao_instituicao: dados.orgao_instituicao || '',
        cpf: dados.cpf || '',
        aceitou_lgpd: dados.aceitou_lgpd,
      }),
    })

    const mapped = mapCredenciado(created, eventoId)
    if (!options?.publico) {
      const evento = getEventoById(eventoId)
      evento?.credenciados.unshift(mapped)
    }
    return mapped
  }

  async function realizarCheckin(eventoId: string, credenciadoId: string) {
    const updated = await apiFetch<CredenciadoApi>(
      `/api/cerimonial/credenciados/${credenciadoId}/checkin/`,
      { method: 'POST' },
    )
    const evento = getEventoById(eventoId)
    const mapped = mapCredenciado(updated, eventoId)
    const idx = evento?.credenciados.findIndex(c => c.id === credenciadoId) ?? -1
    if (evento && idx >= 0) evento.credenciados[idx] = mapped
    return mapped
  }

  const totalCredenciados = computed(() => (eventoId: string) => {
    return getEventoById(eventoId)?.credenciados.length ?? 0
  })

  const totalPresentes = computed(() => (eventoId: string) => {
    const evento = getEventoById(eventoId)
    return evento?.credenciados.filter(c => c.status_presenca === 'presente').length ?? 0
  })

  async function enviarComunicacao(
    eventoId: string,
    dados: Omit<ComunicacaoDisparo, 'id' | 'eventoId' | 'dataHora' | 'status'>,
  ) {
    const created = await apiFetch<ComunicacaoApi>('/api/cerimonial/comunicacoes/', {
      method: 'POST',
      body: JSON.stringify({
        evento_id: Number(eventoId),
        canal: dados.canal,
        mensagem: dados.mensagem,
        publico_alvo: {
          convidados: dados.publicoAlvo.convidados,
          tagsCrm: dados.publicoAlvo.tagsCrm,
          quantidade_estimada: dados.quantidadeEnvios,
        },
        quantidade_envios: dados.quantidadeEnvios,
      }),
    })
    const mapped = mapComunicacao(created, eventoId)
    const evento = getEventoById(eventoId)
    evento?.comunicacoes.unshift(mapped)
    return mapped
  }

  async function criarEvento(
    dados: Omit<
      Evento,
      'id' | 'createdAt' | 'checklist' | 'convidados' | 'credenciados' | 'comunicacoes' | 'credenciamentoConfig'
    >,
  ) {
    const { useAgendaStore } = await import('./agenda')
    const agendaStore = useAgendaStore()
    if (agendaStore.tiposEvento.length === 0) {
      await agendaStore.fetchTiposEvento()
    }
    const tipoPadrao =
      agendaStore.tiposEvento.find(t =>
        t.nome.toLowerCase().includes('cerimônia') || t.nome.toLowerCase().includes('cerimonial'),
      ) ?? agendaStore.tiposEventoAtivos[0]

    if (!tipoPadrao) {
      throw new ApiError('Cadastre ao menos um tipo de evento na Agenda.', 400)
    }

    const created = await apiFetch<EventoCerimonialApi>('/api/cerimonial/eventos/', {
      method: 'POST',
      body: JSON.stringify({
        titulo: dados.titulo,
        descricao: dados.descricao || '',
        data: dados.data,
        hora_inicio: dados.horaInicio,
        hora_fim: dados.horaFim || dados.horaInicio,
        tipo_id: Number(tipoPadrao.id),
        local: dados.local,
        status_logistico: mapStatusToApi(dados.status),
      }),
    })

    const mapped = mapEventoFromApi(created, true)
    upsertEvento(mapped, true)
    return mapped
  }

  function urlLogisticaPublica(token: string) {
    return `${window.location.origin}/evento/logistica/${token}`
  }

  async function ativarLinkLogistica(eventoId: string) {
    const data = await apiFetch<{ token: string; logistica_publica_ativa: boolean }>(
      `/api/cerimonial/eventos/${eventoId}/ativar-link-logistica/`,
      { method: 'POST' },
    )
    const evento = getEventoById(eventoId)
    if (evento) {
      evento.tokenLogistica = data.token
      evento.logisticaPublicaAtiva = data.logistica_publica_ativa
    }
    return data
  }

  async function revogarLinkLogistica(eventoId: string) {
    await apiFetch(`/api/cerimonial/eventos/${eventoId}/revogar-link-logistica/`, {
      method: 'POST',
    })
    const evento = getEventoById(eventoId)
    if (evento) {
      evento.logisticaPublicaAtiva = false
    }
  }

  async function fetchLogisticaPublica(token: string) {
    return apiFetch<{
      titulo: string
      data: string
      local: string
      status_logistico: string
      checklist: ItemChecklistApi[]
    }>(`/api/cerimonial/logistica-publica/${token}/`, { skipAuth: true })
  }

  async function enviarLogisticaPublica(
    token: string,
    payload: {
      itens: Array<{
        id: number
        responsavel?: string
        prazo?: string | null
        observacoes?: string
        status?: ItemChecklist['status']
        descartar?: boolean
      }>
      observacao_envio?: string
    },
  ) {
    return apiFetch<{ ok: boolean; mensagem: string; checklist: ItemChecklistApi[] }>(
      `/api/cerimonial/logistica-publica/${token}/enviar/`,
      {
        method: 'POST',
        skipAuth: true,
        body: JSON.stringify(payload),
      },
    )
  }

  async function excluirEvento(eventoId: string) {
    await apiFetch(`/api/cerimonial/eventos/${eventoId}/`, {
      method: 'DELETE',
      parseJson: false,
    })
    eventos.value = eventos.value.filter(e => e.id !== eventoId)
    await fetchResumo()
  }

  return {
    eventos,
    eventosListagem,
    itensPadrao,
    loading,
    listLoading,
    eventoPublico,
    resumo,
    listTotal,
    listPage,
    listPageSize,
    listFiltroStatus,
    listBusca,
    initialize,
    fetchEventos,
    fetchEventosPagina,
    fetchResumo,
    setListFiltros,
    recarregarListagem,
    fetchChecklistPadrao,
    fetchEventoDashboard,
    atualizarCredenciamentoConfig,
    DEFAULT_CREDENCIAMENTO_CONFIG,
    fetchEventoPublico,
    getEventoById,
    criarEvento,
    excluirEvento,
    toggleItemChecklist,
    adicionarItemChecklist,
    removerItemChecklist,
    checklistPorCategoria,
    progressoChecklist,
    adicionarItemPadrao,
    removerItemPadrao,
    adicionarItemPadraoAoEvento,
    itensPadraoPorCategoria,
    adicionarConvidado,
    atualizarConvidado,
    removerConvidado,
    atualizarOrdemPrecedencia,
    salvarOrdemConvidados,
    convidadosOrdenados,
    convidadosConfirmados,
    registrarCredenciamento,
    realizarCheckin,
    totalCredenciados,
    totalPresentes,
    enviarComunicacao,
    urlLogisticaPublica,
    ativarLinkLogistica,
    revogarLinkLogistica,
    fetchLogisticaPublica,
    enviarLogisticaPublica,
  }
})
