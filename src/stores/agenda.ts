import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ApiError, apiFetch } from '@/services/api'
import { mapRastreabilidade, type RastreabilidadeApi } from '@/utils/rastreabilidade'

// ==================== TIPOS ====================
export interface TipoEvento {
  id: string
  nome: string
  cor: string
  icone?: string
  descricao?: string
  ativo: boolean
  createdAt?: string
  rastreabilidade?: import('@/utils/rastreabilidade').Rastreabilidade | null
}

export interface Espaco {
  id: string
  nome: string
  descricao?: string
  capacidade: number
  icone: string
  cor: string
  ativo: boolean
  createdAt: string
  rastreabilidade?: import('@/utils/rastreabilidade').Rastreabilidade | null
}

export interface ConvidadoEventoResumo {
  id: string
  nome: string
  cpf?: string
  email?: string
  avatar?: string
  telefone?: string
}

export interface Evento {
  id: string
  titulo: string
  descricao?: string
  tipoId: string
  data: string
  horaInicio: string
  horaFim: string
  espacoId?: string
  convidadosIds: string[]
  convidadosResumo?: ConvidadoEventoResumo[]
  criadoPor: string
  status: 'agendado' | 'realizado' | 'cancelado'
  isSyncedGoogle?: boolean
  isSyncedOutlook?: boolean
  createdAt: string
  rastreabilidade?: import('@/utils/rastreabilidade').Rastreabilidade | null
}

export interface ConflictCheck {
  hasConflict: boolean
  conflictingEvent?: Evento
}

interface DrfPaginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

interface TipoEventoApi {
  id: number
  nome: string
  cor: string
  icone: string
  descricao?: string
  ativo: boolean
  rastreabilidade?: RastreabilidadeApi
}

interface EspacoApi {
  id: number
  nome: string
  descricao?: string
  capacidade: number
  icone: string
  cor: string
  ativo: boolean
  created_at: string
  rastreabilidade?: RastreabilidadeApi
}

interface EventoApi {
  id: number
  titulo: string
  descricao?: string
  data: string
  hora_inicio: string
  hora_fim: string
  tipo: TipoEventoApi
  espaco?: EspacoApi | null
  convidados?: Array<{
    id: number
    nome: string
    cpf?: string | null
    email?: string
    avatar?: string
    telefone?: string
  }>
  is_synced_google: boolean
  is_synced_outlook: boolean
  status: Evento['status']
  criado_por?: { id: number; nome: string } | null
  created_at: string
  rastreabilidade?: RastreabilidadeApi
}

function horaFromApi(value: string): string {
  return value.length >= 5 ? value.slice(0, 5) : value
}

function horaToApi(value: string): string {
  return value.length === 5 ? `${value}:00` : value
}

function mapTipoFromApi(t: TipoEventoApi): TipoEvento {
  return {
    id: String(t.id),
    nome: t.nome,
    cor: t.cor,
    icone: t.icone,
    descricao: t.descricao,
    ativo: t.ativo,
    rastreabilidade: mapRastreabilidade(t.rastreabilidade),
  }
}

function mapEspacoFromApi(e: EspacoApi): Espaco {
  return {
    id: String(e.id),
    nome: e.nome,
    descricao: e.descricao,
    capacidade: e.capacidade,
    icone: e.icone,
    cor: e.cor,
    ativo: e.ativo,
    createdAt: e.created_at,
    rastreabilidade: mapRastreabilidade(e.rastreabilidade),
  }
}

function mapEventoFromApi(item: EventoApi): Evento {
  return {
    id: String(item.id),
    titulo: item.titulo,
    descricao: item.descricao,
    tipoId: String(item.tipo.id),
    data: item.data,
    horaInicio: horaFromApi(item.hora_inicio),
    horaFim: horaFromApi(item.hora_fim),
    espacoId: item.espaco ? String(item.espaco.id) : undefined,
    convidadosIds: (item.convidados ?? []).map(c => String(c.id)),
    convidadosResumo: (item.convidados ?? []).map(c => ({
      id: String(c.id),
      nome: c.nome,
      cpf: c.cpf ?? undefined,
      email: c.email,
      avatar: c.avatar,
      telefone: c.telefone,
    })),
    criadoPor: item.criado_por?.nome ?? '—',
    status: item.status,
    isSyncedGoogle: item.is_synced_google,
    isSyncedOutlook: item.is_synced_outlook,
    createdAt: item.created_at,
    rastreabilidade: mapRastreabilidade(item.rastreabilidade),
  }
}

export function getAgendaApiErrorMessage(error: unknown): string {
  if (!(error instanceof ApiError)) {
    return error instanceof Error ? error.message : 'Erro desconhecido'
  }
  const data = error.data
  if (typeof data === 'object' && data !== null) {
    const record = data as Record<string, unknown>
    if (record.espaco) {
      return Array.isArray(record.espaco) ? String(record.espaco[0]) : String(record.espaco)
    }
    if (record.hora_fim) {
      return Array.isArray(record.hora_fim) ? String(record.hora_fim[0]) : String(record.hora_fim)
    }
    if (record.non_field_errors) {
      const errs = record.non_field_errors as unknown[]
      if (errs.length) return String(errs[0])
    }
    if (record.detail) {
      return String(record.detail)
    }
  }
  return error.message
}

function eventoToPayload(data: Partial<Evento>): Record<string, unknown> {
  return {
    titulo: data.titulo,
    descricao: data.descricao ?? '',
    data: data.data,
    hora_inicio: data.horaInicio ? horaToApi(data.horaInicio) : undefined,
    hora_fim: data.horaFim ? horaToApi(data.horaFim) : undefined,
    tipo_id: data.tipoId ? Number(data.tipoId) : undefined,
    espaco_id: data.espacoId ? Number(data.espacoId) : null,
    convidado_ids: (data.convidadosIds ?? []).map(id => Number(id)),
    status: data.status ?? 'agendado',
    is_synced_google: data.isSyncedGoogle ?? false,
    is_synced_outlook: data.isSyncedOutlook ?? false,
  }
}

// ==================== STORE ====================
export const useAgendaStore = defineStore('agenda', () => {
  const tiposEvento = ref<TipoEvento[]>([])
  const espacos = ref<Espaco[]>([])
  const eventos = ref<Evento[]>([])
  const loading = ref(false)

  const tiposEventoAtivos = computed(() => tiposEvento.value.filter(t => t.ativo))

  const espacosAtivos = computed(() => espacos.value.filter(e => e.ativo))

  const eventosAgrupados = computed(() => {
    const grupos: Record<string, Evento[]> = {}

    eventos.value
      .filter(e => e.status === 'agendado')
      .forEach(evento => {
        if (!grupos[evento.data]) {
          grupos[evento.data] = []
        }
        grupos[evento.data].push(evento)
      })

    Object.keys(grupos).forEach(data => {
      grupos[data].sort((a, b) => a.horaInicio.localeCompare(b.horaInicio))
    })

    return grupos
  })

  async function fetchTiposEvento() {
    const data = await apiFetch<TipoEventoApi[] | DrfPaginated<TipoEventoApi>>(
      '/api/agenda/tipos-evento/',
    )
    const list = Array.isArray(data) ? data : data.results
    tiposEvento.value = list.map(mapTipoFromApi)
  }

  async function fetchEspacos() {
    const data = await apiFetch<EspacoApi[] | DrfPaginated<EspacoApi>>('/api/agenda/espacos/')
    const list = Array.isArray(data) ? data : data.results
    espacos.value = list.map(mapEspacoFromApi)
  }

  async function fetchEventos(params?: { dataDe?: string; dataAte?: string }) {
    const search = new URLSearchParams({ page_size: '500' })
    if (params?.dataDe) search.set('data_de', params.dataDe)
    if (params?.dataAte) search.set('data_ate', params.dataAte)

    const aggregated: Evento[] = []
    let page = 1
    let hasNext = true

    while (hasNext) {
      search.set('page', String(page))
      const response = await apiFetch<DrfPaginated<EventoApi>>(
        `/api/agenda/eventos/?${search.toString()}`,
      )
      aggregated.push(...response.results.map(mapEventoFromApi))
      hasNext = Boolean(response.next)
      page += 1
      if (page > 20) break
    }

    eventos.value = aggregated
    return aggregated
  }

  async function initialize() {
    loading.value = true
    try {
      await Promise.all([fetchTiposEvento(), fetchEspacos(), fetchEventos()])
    } finally {
      loading.value = false
    }
  }

  function checkConflict(
    espacoId: string | undefined,
    data: string,
    horaInicio: string,
    horaFim: string,
    eventoIdExcluir?: string,
  ): ConflictCheck {
    if (!espacoId) {
      return { hasConflict: false }
    }

    const eventosNoEspaco = eventos.value.filter(
      e =>
        e.espacoId === espacoId &&
        e.data === data &&
        e.status === 'agendado' &&
        e.id !== eventoIdExcluir,
    )

    for (const evento of eventosNoEspaco) {
      const [h1, m1] = horaInicio.split(':').map(Number)
      const [h2, m2] = horaFim.split(':').map(Number)
      const [h3, m3] = evento.horaInicio.split(':').map(Number)
      const [h4, m4] = evento.horaFim.split(':').map(Number)

      const inicio1 = h1 * 60 + m1
      const fim1 = h2 * 60 + m2
      const inicio2 = h3 * 60 + m3
      const fim2 = h4 * 60 + m4

      if (inicio1 < fim2 && fim1 > inicio2) {
        return { hasConflict: true, conflictingEvent: evento }
      }
    }

    return { hasConflict: false }
  }

  async function createEvento(data: Omit<Evento, 'id' | 'createdAt'>) {
    loading.value = true
    try {
      const created = await apiFetch<EventoApi>('/api/agenda/eventos/', {
        method: 'POST',
        body: JSON.stringify(eventoToPayload(data)),
      })
      const mapped = mapEventoFromApi(created)
      eventos.value.push(mapped)
      return mapped
    } finally {
      loading.value = false
    }
  }

  async function updateEvento(id: string, data: Partial<Evento>) {
    loading.value = true
    try {
      const updated = await apiFetch<EventoApi>(`/api/agenda/eventos/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(eventoToPayload(data)),
      })
      const mapped = mapEventoFromApi(updated)
      const index = eventos.value.findIndex(e => e.id === id)
      if (index >= 0) {
        eventos.value[index] = mapped
      }
      return true
    } finally {
      loading.value = false
    }
  }

  async function deleteEvento(id: string) {
    loading.value = true
    try {
      await apiFetch(`/api/agenda/eventos/${id}/`, {
        method: 'DELETE',
        parseJson: false,
      })
      eventos.value = eventos.value.filter(e => e.id !== id)
      return true
    } finally {
      loading.value = false
    }
  }

  async function cancelarEvento(id: string) {
    return updateEvento(id, { status: 'cancelado' })
  }

  async function createEspaco(data: Omit<Espaco, 'id' | 'createdAt'>) {
    const created = await apiFetch<EspacoApi>('/api/agenda/espacos/', {
      method: 'POST',
      body: JSON.stringify({
        nome: data.nome,
        descricao: data.descricao ?? '',
        capacidade: data.capacidade,
        icone: data.icone,
        cor: data.cor,
        ativo: data.ativo,
      }),
    })
    const mapped = mapEspacoFromApi(created)
    espacos.value.push(mapped)
    return mapped
  }

  async function updateEspaco(id: string, data: Partial<Espaco>) {
    const updated = await apiFetch<EspacoApi>(`/api/agenda/espacos/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify({
        nome: data.nome,
        descricao: data.descricao,
        capacidade: data.capacidade,
        icone: data.icone,
        cor: data.cor,
        ativo: data.ativo,
      }),
    })
    const mapped = mapEspacoFromApi(updated)
    const index = espacos.value.findIndex(e => e.id === id)
    if (index >= 0) {
      espacos.value[index] = mapped
    }
    return true
  }

  async function deleteEspaco(id: string) {
    try {
      await apiFetch(`/api/agenda/espacos/${id}/`, {
        method: 'DELETE',
        parseJson: false,
      })
      espacos.value = espacos.value.filter(e => e.id !== id)
      return true
    } catch (error) {
      throw new Error(getAgendaApiErrorMessage(error))
    }
  }

  async function createTipoEvento(data: Omit<TipoEvento, 'id' | 'createdAt'>) {
    const created = await apiFetch<TipoEventoApi>('/api/agenda/tipos-evento/', {
      method: 'POST',
      body: JSON.stringify({
        nome: data.nome,
        cor: data.cor,
        icone: data.icone ?? 'calendar',
        descricao: data.descricao ?? '',
        ativo: data.ativo,
      }),
    })
    const mapped = mapTipoFromApi(created)
    tiposEvento.value.push(mapped)
    return mapped
  }

  async function updateTipoEvento(id: string, data: Partial<TipoEvento>) {
    const updated = await apiFetch<TipoEventoApi>(`/api/agenda/tipos-evento/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify({
        nome: data.nome,
        cor: data.cor,
        icone: data.icone,
        descricao: data.descricao,
        ativo: data.ativo,
      }),
    })
    const mapped = mapTipoFromApi(updated)
    const index = tiposEvento.value.findIndex(t => t.id === id)
    if (index >= 0) {
      tiposEvento.value[index] = mapped
    }
    return true
  }

  async function deleteTipoEvento(id: string) {
    try {
      await apiFetch(`/api/agenda/tipos-evento/${id}/`, {
        method: 'DELETE',
        parseJson: false,
      })
      tiposEvento.value = tiposEvento.value.filter(t => t.id !== id)
      return true
    } catch (error) {
      throw new Error(getAgendaApiErrorMessage(error))
    }
  }

  function getTipoEventoById(id: string): TipoEvento | undefined {
    return tiposEvento.value.find(t => t.id === id)
  }

  function getEspacoById(id: string): Espaco | undefined {
    return espacos.value.find(e => e.id === id)
  }

  function getEventoById(id: string): Evento | undefined {
    return eventos.value.find(e => e.id === id)
  }

  function getEventosByData(data: string): Evento[] {
    return eventos.value
      .filter(e => e.data === data && e.status === 'agendado')
      .sort((a, b) => a.horaInicio.localeCompare(b.horaInicio))
  }

  function getEventosByEspaco(espacoId: string): Evento[] {
    return eventos.value
      .filter(e => e.espacoId === espacoId && e.status === 'agendado')
      .sort((a, b) => {
        if (a.data !== b.data) return a.data.localeCompare(b.data)
        return a.horaInicio.localeCompare(b.horaInicio)
      })
  }

  return {
    tiposEvento,
    espacos,
    eventos,
    loading,
    tiposEventoAtivos,
    espacosAtivos,
    eventosAgrupados,
    initialize,
    fetchTiposEvento,
    fetchEspacos,
    fetchEventos,
    checkConflict,
    createTipoEvento,
    updateTipoEvento,
    deleteTipoEvento,
    createEvento,
    criarEvento: createEvento,
    updateEvento,
    deleteEvento,
    cancelarEvento,
    createEspaco,
    updateEspaco,
    deleteEspaco,
    getTipoEventoById,
    getEspacoById,
    getEventoById,
    getEventosByData,
    getEventosByEspaco,
    getAgendaApiErrorMessage,
  }
})
