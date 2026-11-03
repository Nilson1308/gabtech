import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
  CandidaturaTalento,
  EixoServico,
  EntregaBeneficio,
  InscricaoCurso,
  ItemBeneficio,
  StatusProcessoTalento,
  StatusVagaEmprego,
  SugestaoMatchmaking,
  TurmaCurso,
  VagaEmprego,
} from '@/types'
import { ApiError, apiFetch } from '@/services/api'
import { mapRastreabilidade, type RastreabilidadeApi } from '@/utils/rastreabilidade'

interface EixoServicoApi {
  id: number
  nome: string
  icone: string
  cor: string
  ativo: boolean
  created_at: string
}

interface TagResumoApi {
  id: number
  nome: string
  cor: string
}

interface VagaEmpregoApi {
  id: number
  eixo: number
  eixo_nome?: string
  titulo: string
  empresa_parceira: string
  descricao: string
  requisitos: string
  status: StatusVagaEmprego
  tags_alvo?: TagResumoApi[]
  etiquetas?: TagResumoApi[]
  created_at: string
  updated_at: string
  rastreabilidade?: RastreabilidadeApi
}

interface CurriculoApi {
  id: number
  nome_original: string
  url_download: string
  created_at?: string
  etiquetas?: TagResumoApi[]
}

interface CandidaturaTalentoApi {
  id: number
  vaga: number
  vaga_titulo?: string
  candidato: {
    id: number
    nome: string
    telefone: string
    email?: string
    bairro?: string
  }
  status_processo: StatusProcessoTalento
  observacoes: string
  curriculo: CurriculoApi | null
  created_at: string
  updated_at: string
  rastreabilidade?: RastreabilidadeApi
}

interface SugestaoApi {
  score: number
  tags_coincidentes: TagResumoApi[]
  cidadao: {
    id: number
    nome: string
    telefone: string
    email?: string
    bairro?: string
  }
}

interface ItemBeneficioApi {
  id: number
  nome: string
  descricao: string
  exige_laudo: boolean
  tags_alvo?: TagResumoApi[]
  created_at: string
  rastreabilidade?: RastreabilidadeApi
}

interface EntregaBeneficioApi {
  id: number
  cidadao: number
  cidadao_nome?: string
  item: number
  item_nome?: string
  data_entrega: string
  quantidade: number
  created_at: string
  rastreabilidade?: RastreabilidadeApi
}

interface TurmaCursoApi {
  id: number
  nome_curso: string
  vagas_totais: number
  vagas_ocupadas: number
  status: TurmaCurso['status']
  tags_alvo?: TagResumoApi[]
  created_at: string
  rastreabilidade?: RastreabilidadeApi
}

interface InscricaoCursoApi {
  id: number
  turma: number
  turma_nome?: string
  cidadao: number
  cidadao_nome?: string
  status: InscricaoCurso['status']
  created_at: string
  rastreabilidade?: RastreabilidadeApi
}

function mapTagResumo(item: TagResumoApi) {
  return { id: String(item.id), nome: item.nome, cor: item.cor }
}

function mapTagsFromVagaApi(item: VagaEmpregoApi) {
  const tags = (item.tags_alvo ?? item.etiquetas ?? []).map(mapTagResumo)
  return tags
}

function mapEixo(item: EixoServicoApi): EixoServico {
  return {
    id: String(item.id),
    nome: item.nome,
    icone: item.icone,
    cor: item.cor,
    ativo: item.ativo,
  }
}

function mapVaga(item: VagaEmpregoApi): VagaEmprego {
  const tagsAlvo = mapTagsFromVagaApi(item)
  return {
    id: String(item.id),
    eixoId: String(item.eixo),
    eixoNome: item.eixo_nome,
    titulo: item.titulo,
    empresaParceira: item.empresa_parceira,
    descricao: item.descricao,
    requisitos: item.requisitos,
    status: item.status,
    tagsAlvo,
    tagsAlvoIds: tagsAlvo.map(e => e.id),
    etiquetas: tagsAlvo,
    etiquetaIds: tagsAlvo.map(e => e.id),
    createdAt: item.created_at,
    updatedAt: item.updated_at,
    rastreabilidade: mapRastreabilidade(item.rastreabilidade),
  }
}

function mapSugestao(item: SugestaoApi): SugestaoMatchmaking {
  return {
    score: item.score,
    tagsCoincidentes: (item.tags_coincidentes ?? []).map(mapTagResumo),
    cidadao: {
      id: String(item.cidadao.id),
      nome: item.cidadao.nome,
      telefone: item.cidadao.telefone,
      email: item.cidadao.email,
      bairro: item.cidadao.bairro,
    },
  }
}

function mapCandidatura(item: CandidaturaTalentoApi): CandidaturaTalento {
  return {
    id: String(item.id),
    vagaId: String(item.vaga),
    vagaTitulo: item.vaga_titulo,
    candidatoId: String(item.candidato.id),
    candidato: {
      id: String(item.candidato.id),
      nome: item.candidato.nome,
      telefone: item.candidato.telefone,
      email: item.candidato.email,
      bairro: item.candidato.bairro,
    },
    statusProcesso: item.status_processo,
    observacoes: item.observacoes ?? '',
    curriculo: item.curriculo
      ? {
          id: String(item.curriculo.id),
          nomeOriginal: item.curriculo.nome_original,
          urlDownload: item.curriculo.url_download,
          createdAt: item.curriculo.created_at,
          etiquetas: (item.curriculo.etiquetas ?? []).map(mapTagResumo),
        }
      : null,
    createdAt: item.created_at,
    updatedAt: item.updated_at,
    rastreabilidade: mapRastreabilidade(item.rastreabilidade),
  }
}

function mapItemBeneficio(item: ItemBeneficioApi): ItemBeneficio {
  const tagsAlvo = (item.tags_alvo ?? []).map(mapTagResumo)
  return {
    id: String(item.id),
    nome: item.nome,
    descricao: item.descricao,
    exigeLaudo: item.exige_laudo,
    tagsAlvo,
    tagsAlvoIds: tagsAlvo.map(t => t.id),
    createdAt: item.created_at,
    rastreabilidade: mapRastreabilidade(item.rastreabilidade),
  }
}

function mapEntrega(item: EntregaBeneficioApi): EntregaBeneficio {
  return {
    id: String(item.id),
    cidadaoId: String(item.cidadao),
    cidadaoNome: item.cidadao_nome,
    itemId: String(item.item),
    itemNome: item.item_nome,
    dataEntrega: item.data_entrega,
    quantidade: item.quantidade,
    createdAt: item.created_at,
    rastreabilidade: mapRastreabilidade(item.rastreabilidade),
  }
}

function mapTurma(item: TurmaCursoApi): TurmaCurso {
  const tagsAlvo = (item.tags_alvo ?? []).map(mapTagResumo)
  return {
    id: String(item.id),
    nomeCurso: item.nome_curso,
    vagasTotais: item.vagas_totais,
    vagasOcupadas: item.vagas_ocupadas,
    status: item.status,
    tagsAlvo,
    tagsAlvoIds: tagsAlvo.map(t => t.id),
    createdAt: item.created_at,
    rastreabilidade: mapRastreabilidade(item.rastreabilidade),
  }
}

function mapInscricao(item: InscricaoCursoApi): InscricaoCurso {
  return {
    id: String(item.id),
    turmaId: String(item.turma),
    turmaNome: item.turma_nome,
    cidadaoId: String(item.cidadao),
    cidadaoNome: item.cidadao_nome,
    status: item.status,
    createdAt: item.created_at,
    rastreabilidade: mapRastreabilidade(item.rastreabilidade),
  }
}

export const useServicosStore = defineStore('servicos', () => {
  const eixos = ref<EixoServico[]>([])
  const vagas = ref<VagaEmprego[]>([])
  const candidaturas = ref<CandidaturaTalento[]>([])
  const itensBeneficio = ref<ItemBeneficio[]>([])
  const entregasBeneficio = ref<EntregaBeneficio[]>([])
  const turmas = ref<TurmaCurso[]>([])
  const inscricoes = ref<InscricaoCurso[]>([])
  const loading = ref(false)

  async function fetchEixos() {
    const data = await apiFetch<EixoServicoApi[]>('/api/servicos/eixos/')
    eixos.value = data.map(mapEixo)
    return eixos.value
  }

  async function fetchVagas(filtros?: { eixoId?: string; status?: StatusVagaEmprego }) {
    const params = new URLSearchParams()
    if (filtros?.eixoId) params.set('eixo', filtros.eixoId)
    if (filtros?.status) params.set('status', filtros.status)
    const qs = params.toString()
    const path = qs ? `/api/servicos/vagas/?${qs}` : '/api/servicos/vagas/'
    const list = await apiFetch<VagaEmpregoApi[]>(path)
    vagas.value = list.map(mapVaga)
    return vagas.value
  }

  async function fetchSugerirCandidatos(vagaId: string, limit = 25): Promise<SugestaoMatchmaking[]> {
    const data = await apiFetch<SugestaoApi[]>(
      `/api/servicos/vagas/${encodeURIComponent(vagaId)}/sugerir_candidatos/?limit=${limit}`,
    )
    return data.map(mapSugestao)
  }

  async function fetchSugerirPublicoBeneficio(itemId: string, limit = 25): Promise<SugestaoMatchmaking[]> {
    const data = await apiFetch<SugestaoApi[]>(
      `/api/servicos/beneficios/itens/${encodeURIComponent(itemId)}/sugerir_publico/?limit=${limit}`,
    )
    return data.map(mapSugestao)
  }

  async function fetchSugerirPublicoTurma(turmaId: string, limit = 25): Promise<SugestaoMatchmaking[]> {
    const data = await apiFetch<SugestaoApi[]>(
      `/api/servicos/cursos/turmas/${encodeURIComponent(turmaId)}/sugerir_publico/?limit=${limit}`,
    )
    return data.map(mapSugestao)
  }

  async function fetchCandidaturas(vagaId?: string) {
    const path = vagaId
      ? `/api/servicos/candidaturas/?vaga=${encodeURIComponent(vagaId)}`
      : '/api/servicos/candidaturas/'
    const data = await apiFetch<
      CandidaturaTalentoApi[] | { results: CandidaturaTalentoApi[] }
    >(path)
    const list = Array.isArray(data) ? data : (data.results ?? [])
    candidaturas.value = list.map(mapCandidatura)
    return candidaturas.value
  }

  async function fetchItensBeneficio() {
    const list = await apiFetch<ItemBeneficioApi[]>('/api/servicos/beneficios/itens/')
    itensBeneficio.value = list.map(mapItemBeneficio)
    return itensBeneficio.value
  }

  async function fetchEntregasBeneficio(cidadaoId?: string) {
    const path = cidadaoId
      ? `/api/servicos/beneficios/entregas/?cidadao=${encodeURIComponent(cidadaoId)}`
      : '/api/servicos/beneficios/entregas/'
    const list = await apiFetch<EntregaBeneficioApi[]>(path)
    entregasBeneficio.value = list.map(mapEntrega)
    return entregasBeneficio.value
  }

  async function fetchTurmas() {
    const list = await apiFetch<TurmaCursoApi[]>('/api/servicos/cursos/turmas/')
    turmas.value = list.map(mapTurma)
    return turmas.value
  }

  async function fetchInscricoes(turmaId?: string) {
    const path = turmaId
      ? `/api/servicos/cursos/inscricoes/?turma=${encodeURIComponent(turmaId)}`
      : '/api/servicos/cursos/inscricoes/'
    const list = await apiFetch<InscricaoCursoApi[]>(path)
    inscricoes.value = list.map(mapInscricao)
    return inscricoes.value
  }

  async function updateStatusCandidatura(
    id: string,
    statusProcesso: StatusProcessoTalento,
  ): Promise<CandidaturaTalento | null> {
    const { candidatura } = await updateCandidatura(id, { statusProcesso })
    return candidatura
  }

  function apiErrorMessage(e: unknown, fallback: string): string {
    return e instanceof ApiError ? e.message : fallback
  }

  async function updateVaga(
    vagaId: string,
    payload: Partial<{
      titulo: string
      empresaParceira: string
      descricao: string
      requisitos: string
      status: StatusVagaEmprego
      tagsAlvoIds: string[]
    }>,
  ): Promise<{ vaga: VagaEmprego | null; erro?: string }> {
    try {
      const body: Record<string, unknown> = {}
      if (payload.titulo !== undefined) body.titulo = payload.titulo
      if (payload.empresaParceira !== undefined) body.empresa_parceira = payload.empresaParceira
      if (payload.descricao !== undefined) body.descricao = payload.descricao
      if (payload.requisitos !== undefined) body.requisitos = payload.requisitos
      if (payload.status !== undefined) body.status = payload.status
      if (payload.tagsAlvoIds !== undefined) {
        body.tags_alvo_ids = payload.tagsAlvoIds.map(id => Number(id))
      }
      const updated = await apiFetch<VagaEmpregoApi>(`/api/servicos/vagas/${vagaId}/`, {
        method: 'PATCH',
        body: JSON.stringify(body),
      })
      const mapped = mapVaga(updated)
      const idx = vagas.value.findIndex(v => v.id === vagaId)
      if (idx >= 0) vagas.value[idx] = mapped
      return { vaga: mapped }
    } catch (e) {
      return { vaga: null, erro: apiErrorMessage(e, 'Não foi possível atualizar a vaga.') }
    }
  }

  async function updateVagaTagsAlvo(vagaId: string, tagsAlvoIds: string[]): Promise<VagaEmprego | null> {
    const { vaga } = await updateVaga(vagaId, { tagsAlvoIds })
    return vaga
  }

  /** @deprecated use updateVagaTagsAlvo */
  const updateVagaEtiquetas = updateVagaTagsAlvo

  async function deleteVaga(vagaId: string): Promise<{ ok: boolean; erro?: string }> {
    try {
      await apiFetch(`/api/servicos/vagas/${vagaId}/`, { method: 'DELETE', parseJson: false })
      vagas.value = vagas.value.filter(v => v.id !== vagaId)
      candidaturas.value = candidaturas.value.filter(c => c.vagaId !== vagaId)
      return { ok: true }
    } catch (e) {
      return { ok: false, erro: apiErrorMessage(e, 'Não foi possível excluir a vaga.') }
    }
  }

  async function updateCandidatura(
    id: string,
    payload: Partial<{ statusProcesso: StatusProcessoTalento; observacoes: string }>,
  ): Promise<{ candidatura: CandidaturaTalento | null; erro?: string }> {
    try {
      const body: Record<string, unknown> = {}
      if (payload.statusProcesso !== undefined) body.status_processo = payload.statusProcesso
      if (payload.observacoes !== undefined) body.observacoes = payload.observacoes
      const updated = await apiFetch<CandidaturaTalentoApi>(`/api/servicos/candidaturas/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(body),
      })
      const mapped = mapCandidatura(updated)
      const idx = candidaturas.value.findIndex(c => c.id === id)
      if (idx >= 0) candidaturas.value[idx] = mapped
      return { candidatura: mapped }
    } catch (e) {
      return { candidatura: null, erro: apiErrorMessage(e, 'Não foi possível atualizar a candidatura.') }
    }
  }

  async function deleteCandidatura(id: string): Promise<{ ok: boolean; erro?: string }> {
    try {
      await apiFetch(`/api/servicos/candidaturas/${id}/`, { method: 'DELETE', parseJson: false })
      candidaturas.value = candidaturas.value.filter(c => c.id !== id)
      return { ok: true }
    } catch (e) {
      return { ok: false, erro: apiErrorMessage(e, 'Não foi possível remover a candidatura.') }
    }
  }

  async function createVaga(payload: {
    eixoId: string
    titulo: string
    empresaParceira: string
    descricao?: string
    requisitos?: string
    status?: StatusVagaEmprego
    tagsAlvoIds?: string[]
    etiquetaIds?: string[]
  }): Promise<VagaEmprego | null> {
    const tagIds = payload.tagsAlvoIds ?? payload.etiquetaIds ?? []
    try {
      const created = await apiFetch<VagaEmpregoApi>('/api/servicos/vagas/', {
        method: 'POST',
        body: JSON.stringify({
          eixo: Number(payload.eixoId),
          titulo: payload.titulo,
          empresa_parceira: payload.empresaParceira,
          descricao: payload.descricao ?? '',
          requisitos: payload.requisitos ?? '',
          status: payload.status ?? 'aberta',
          tags_alvo_ids: tagIds.map(id => Number(id)),
        }),
      })
      const mapped = mapVaga(created)
      vagas.value.unshift(mapped)
      return mapped
    } catch {
      return null
    }
  }

  async function updateItemBeneficio(
    itemId: string,
    payload: Partial<{
      nome: string
      descricao: string
      exigeLaudo: boolean
      tagsAlvoIds: string[]
    }>,
  ): Promise<{ item: ItemBeneficio | null; erro?: string }> {
    try {
      const body: Record<string, unknown> = {}
      if (payload.nome !== undefined) body.nome = payload.nome
      if (payload.descricao !== undefined) body.descricao = payload.descricao
      if (payload.exigeLaudo !== undefined) body.exige_laudo = payload.exigeLaudo
      if (payload.tagsAlvoIds !== undefined) {
        body.tags_alvo_ids = payload.tagsAlvoIds.map(id => Number(id))
      }
      const updated = await apiFetch<ItemBeneficioApi>(
        `/api/servicos/beneficios/itens/${itemId}/`,
        { method: 'PATCH', body: JSON.stringify(body) },
      )
      const mapped = mapItemBeneficio(updated)
      const idx = itensBeneficio.value.findIndex(i => i.id === itemId)
      if (idx >= 0) itensBeneficio.value[idx] = mapped
      return { item: mapped }
    } catch (e) {
      return { item: null, erro: apiErrorMessage(e, 'Não foi possível atualizar o item.') }
    }
  }

  async function deleteItemBeneficio(itemId: string): Promise<{ ok: boolean; erro?: string }> {
    try {
      await apiFetch(`/api/servicos/beneficios/itens/${itemId}/`, {
        method: 'DELETE',
        parseJson: false,
      })
      itensBeneficio.value = itensBeneficio.value.filter(i => i.id !== itemId)
      return { ok: true }
    } catch (e) {
      return {
        ok: false,
        erro: apiErrorMessage(
          e,
          'Não foi possível excluir o item (pode haver entregas vinculadas).',
        ),
      }
    }
  }

  async function createItemBeneficio(payload: {
    nome: string
    descricao?: string
    exigeLaudo?: boolean
    tagsAlvoIds?: string[]
  }): Promise<ItemBeneficio | null> {
    try {
      const created = await apiFetch<ItemBeneficioApi>('/api/servicos/beneficios/itens/', {
        method: 'POST',
        body: JSON.stringify({
          nome: payload.nome,
          descricao: payload.descricao ?? '',
          exige_laudo: payload.exigeLaudo ?? false,
          tags_alvo_ids: (payload.tagsAlvoIds ?? []).map(id => Number(id)),
        }),
      })
      const mapped = mapItemBeneficio(created)
      itensBeneficio.value.unshift(mapped)
      return mapped
    } catch {
      return null
    }
  }

  async function updateEntregaBeneficio(
    entregaId: string,
    payload: Partial<{ dataEntrega: string; quantidade: number }>,
  ): Promise<{ entrega: EntregaBeneficio | null; erro?: string }> {
    try {
      const body: Record<string, unknown> = {}
      if (payload.dataEntrega !== undefined) body.data_entrega = payload.dataEntrega
      if (payload.quantidade !== undefined) body.quantidade = payload.quantidade
      const updated = await apiFetch<EntregaBeneficioApi>(
        `/api/servicos/beneficios/entregas/${entregaId}/`,
        { method: 'PATCH', body: JSON.stringify(body) },
      )
      const mapped = mapEntrega(updated)
      const idx = entregasBeneficio.value.findIndex(e => e.id === entregaId)
      if (idx >= 0) entregasBeneficio.value[idx] = mapped
      return { entrega: mapped }
    } catch (e) {
      return { entrega: null, erro: apiErrorMessage(e, 'Não foi possível atualizar a entrega.') }
    }
  }

  async function deleteEntregaBeneficio(entregaId: string): Promise<{ ok: boolean; erro?: string }> {
    try {
      await apiFetch(`/api/servicos/beneficios/entregas/${entregaId}/`, {
        method: 'DELETE',
        parseJson: false,
      })
      entregasBeneficio.value = entregasBeneficio.value.filter(e => e.id !== entregaId)
      return { ok: true }
    } catch (e) {
      return { ok: false, erro: apiErrorMessage(e, 'Não foi possível excluir a entrega.') }
    }
  }

  async function createEntregaBeneficio(payload: {
    cidadaoId: string
    itemId: string
    dataEntrega: string
    quantidade?: number
  }): Promise<{ entrega: EntregaBeneficio | null; erro?: string }> {
    try {
      const created = await apiFetch<EntregaBeneficioApi>('/api/servicos/beneficios/entregas/', {
        method: 'POST',
        body: JSON.stringify({
          cidadao: Number(payload.cidadaoId),
          item: Number(payload.itemId),
          data_entrega: payload.dataEntrega,
          quantidade: payload.quantidade ?? 1,
        }),
      })
      const mapped = mapEntrega(created)
      entregasBeneficio.value.unshift(mapped)
      return { entrega: mapped }
    } catch (e) {
      const msg =
        e instanceof ApiError ? e.message : 'Não foi possível registrar a entrega.'
      return { entrega: null, erro: msg }
    }
  }

  async function updateTurma(
    turmaId: string,
    payload: Partial<{
      nomeCurso: string
      vagasTotais: number
      status: TurmaCurso['status']
      tagsAlvoIds: string[]
    }>,
  ): Promise<{ turma: TurmaCurso | null; erro?: string }> {
    try {
      const body: Record<string, unknown> = {}
      if (payload.nomeCurso !== undefined) body.nome_curso = payload.nomeCurso
      if (payload.vagasTotais !== undefined) body.vagas_totais = payload.vagasTotais
      if (payload.status !== undefined) body.status = payload.status
      if (payload.tagsAlvoIds !== undefined) {
        body.tags_alvo_ids = payload.tagsAlvoIds.map(id => Number(id))
      }
      const updated = await apiFetch<TurmaCursoApi>(`/api/servicos/cursos/turmas/${turmaId}/`, {
        method: 'PATCH',
        body: JSON.stringify(body),
      })
      const mapped = mapTurma(updated)
      const idx = turmas.value.findIndex(t => t.id === turmaId)
      if (idx >= 0) turmas.value[idx] = mapped
      return { turma: mapped }
    } catch (e) {
      return { turma: null, erro: apiErrorMessage(e, 'Não foi possível atualizar a turma.') }
    }
  }

  async function deleteTurma(turmaId: string): Promise<{ ok: boolean; erro?: string }> {
    try {
      await apiFetch(`/api/servicos/cursos/turmas/${turmaId}/`, {
        method: 'DELETE',
        parseJson: false,
      })
      turmas.value = turmas.value.filter(t => t.id !== turmaId)
      inscricoes.value = inscricoes.value.filter(i => i.turmaId !== turmaId)
      return { ok: true }
    } catch (e) {
      return { ok: false, erro: apiErrorMessage(e, 'Não foi possível excluir a turma.') }
    }
  }

  async function createTurma(payload: {
    nomeCurso: string
    vagasTotais?: number
    tagsAlvoIds?: string[]
  }): Promise<TurmaCurso | null> {
    try {
      const created = await apiFetch<TurmaCursoApi>('/api/servicos/cursos/turmas/', {
        method: 'POST',
        body: JSON.stringify({
          nome_curso: payload.nomeCurso,
          vagas_totais: payload.vagasTotais ?? 20,
          tags_alvo_ids: (payload.tagsAlvoIds ?? []).map(id => Number(id)),
        }),
      })
      const mapped = mapTurma(created)
      turmas.value.unshift(mapped)
      return mapped
    } catch {
      return null
    }
  }

  async function updateInscricaoCurso(
    inscricaoId: string,
    payload: Partial<{ status: InscricaoCurso['status'] }>,
  ): Promise<{ inscricao: InscricaoCurso | null; erro?: string }> {
    try {
      const updated = await apiFetch<InscricaoCursoApi>(
        `/api/servicos/cursos/inscricoes/${inscricaoId}/`,
        {
          method: 'PATCH',
          body: JSON.stringify({ status: payload.status }),
        },
      )
      const mapped = mapInscricao(updated)
      const idx = inscricoes.value.findIndex(i => i.id === inscricaoId)
      if (idx >= 0) inscricoes.value[idx] = mapped
      await fetchTurmas()
      return { inscricao: mapped }
    } catch (e) {
      return { inscricao: null, erro: apiErrorMessage(e, 'Não foi possível atualizar a inscrição.') }
    }
  }

  async function deleteInscricaoCurso(inscricaoId: string): Promise<{ ok: boolean; erro?: string }> {
    try {
      await apiFetch(`/api/servicos/cursos/inscricoes/${inscricaoId}/`, {
        method: 'DELETE',
        parseJson: false,
      })
      inscricoes.value = inscricoes.value.filter(i => i.id !== inscricaoId)
      await fetchTurmas()
      return { ok: true }
    } catch (e) {
      return { ok: false, erro: apiErrorMessage(e, 'Não foi possível remover a inscrição.') }
    }
  }

  async function createInscricaoCurso(payload: {
    turmaId: string
    cidadaoId: string
  }): Promise<{ inscricao: InscricaoCurso | null; erro?: string }> {
    try {
      const created = await apiFetch<InscricaoCursoApi>('/api/servicos/cursos/inscricoes/', {
        method: 'POST',
        body: JSON.stringify({
          turma: Number(payload.turmaId),
          cidadao_id: Number(payload.cidadaoId),
        }),
      })
      const mapped = mapInscricao(created)
      inscricoes.value.unshift(mapped)
      return { inscricao: mapped }
    } catch (e) {
      const msg =
        e instanceof ApiError ? e.message : 'Não foi possível inscrever o cidadão.'
      return { inscricao: null, erro: msg }
    }
  }

  async function createCandidatura(payload: {
    vagaId: string
    candidatoId: string
    observacoes?: string
  }): Promise<{ candidatura: CandidaturaTalento | null; erro?: string }> {
    try {
      const created = await apiFetch<CandidaturaTalentoApi>('/api/servicos/candidaturas/', {
        method: 'POST',
        body: JSON.stringify({
          vaga: Number(payload.vagaId),
          candidato_id: Number(payload.candidatoId),
          observacoes: payload.observacoes ?? '',
        }),
      })
      const mapped = mapCandidatura(created)
      candidaturas.value.unshift(mapped)
      return { candidatura: mapped }
    } catch (e) {
      if (e instanceof ApiError && e.status === 400) {
        return {
          candidatura: null,
          erro: 'Este cidadão já está inscrito nesta vaga.',
        }
      }
      return { candidatura: null, erro: 'Não foi possível vincular o candidato.' }
    }
  }

  async function carregarBancoTalentos(vagaId?: string) {
    loading.value = true
    try {
      await fetchEixos()
      await fetchVagas()
      await fetchCandidaturas(vagaId)
    } finally {
      loading.value = false
    }
  }

  async function carregarAssistenciaSocial() {
    loading.value = true
    try {
      await fetchItensBeneficio()
      await fetchEntregasBeneficio()
    } finally {
      loading.value = false
    }
  }

  async function carregarCursos(turmaId?: string) {
    loading.value = true
    try {
      await fetchTurmas()
      await fetchInscricoes(turmaId)
    } finally {
      loading.value = false
    }
  }

  /** Métricas leves para o dashboard do módulo Serviços. */
  async function carregarResumoModulo() {
    await Promise.all([
      fetchEixos(),
      fetchVagas(),
      fetchCandidaturas(),
      fetchItensBeneficio(),
      fetchEntregasBeneficio(),
      fetchTurmas(),
      fetchInscricoes(),
    ])
  }

  return {
    eixos,
    vagas,
    candidaturas,
    itensBeneficio,
    entregasBeneficio,
    turmas,
    inscricoes,
    loading,
    fetchEixos,
    fetchVagas,
    fetchSugerirCandidatos,
    fetchSugerirPublicoBeneficio,
    fetchSugerirPublicoTurma,
    fetchCandidaturas,
    fetchItensBeneficio,
    fetchEntregasBeneficio,
    fetchTurmas,
    fetchInscricoes,
    updateStatusCandidatura,
    updateVaga,
    deleteVaga,
    updateCandidatura,
    deleteCandidatura,
    createVaga,
    updateVagaTagsAlvo,
    updateVagaEtiquetas,
    createItemBeneficio,
    updateItemBeneficio,
    deleteItemBeneficio,
    createEntregaBeneficio,
    updateEntregaBeneficio,
    deleteEntregaBeneficio,
    createTurma,
    updateTurma,
    deleteTurma,
    createInscricaoCurso,
    updateInscricaoCurso,
    deleteInscricaoCurso,
    createCandidatura,
    carregarBancoTalentos,
    carregarAssistenciaSocial,
    carregarCursos,
    carregarResumoModulo,
  }
})
