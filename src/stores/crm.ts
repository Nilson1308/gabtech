import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Cidadao,
  CidadaoDocumento,
  Tag,
  TipoTag,
  ModuloTag,
  PaginatedResponse,
  PerfilProfissional,
  Endereco,
} from '@/types'
import type { CategoriaDocumentoCidadao } from '@/constants/crmDocumentos'
import { apiDownload, apiFetch, apiUpload } from '@/services/api'
import { arredondarCoordenada } from '@/utils/geocode'
import { mapRastreabilidade, type RastreabilidadeApi } from '@/utils/rastreabilidade'

interface DrfPaginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

interface CidadaoApi {
  id: number
  nome: string
  nome_social?: string
  cpf?: string | null
  telefone: string
  email?: string
  avatar?: string
  observacoes?: string
  bairro?: string
  endereco?: Endereco | null
  perfis_profissionais?: Array<{
    id: number
    instituicao: string
    cargo: string
    tag_id: number | null
  }>
  tag_ids?: number[]
  created_at?: string
  updated_at?: string
  rastreabilidade?: RastreabilidadeApi
}

interface TagApi {
  id: number
  nome: string
  cor: string
  tipo?: TipoTag
  modulos?: ('crm' | 'atendimentos')[]
  rastreabilidade?: RastreabilidadeApi
}

interface TagResumoApi {
  id: number
  nome: string
  cor: string
}

interface DocumentoAnexoApi {
  id: number
  cidadao: number
  categoria: CategoriaDocumentoCidadao
  nome_original: string
  content_type: string
  tamanho: number
  created_at: string
  url_download: string | null
  etiquetas?: TagResumoApi[]
}

function mapTagResumoFromApi(tag: TagResumoApi) {
  return { id: String(tag.id), nome: tag.nome, cor: tag.cor }
}

function mapDocumentoFromApi(item: DocumentoAnexoApi): CidadaoDocumento {
  return {
    id: String(item.id),
    nome: item.nome_original,
    categoria: item.categoria ?? 'outros',
    tipo: item.content_type,
    tamanho: item.tamanho,
    dataUpload: item.created_at,
    urlDownload: item.url_download ?? `/api/crm/documentos/${item.id}/download/`,
    etiquetas: (item.etiquetas ?? []).map(mapTagResumoFromApi),
  }
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

function mapCidadaoFromApi(item: CidadaoApi): Cidadao {
  return {
    id: String(item.id),
    nome: item.nome,
    nome_social: item.nome_social || undefined,
    cpf: item.cpf || undefined,
    telefone: item.telefone,
    email: item.email || undefined,
    avatar: item.avatar || undefined,
    bairro: item.bairro || item.endereco?.bairro,
    endereco: item.endereco
      ? {
          logradouro: item.endereco.logradouro,
          numero: item.endereco.numero,
          complemento: item.endereco.complemento,
          bairro: item.endereco.bairro,
          cidade: item.endereco.cidade,
          estado: item.endereco.estado,
          cep: item.endereco.cep,
          latitude: item.endereco.latitude != null ? Number(item.endereco.latitude) : undefined,
          longitude: item.endereco.longitude != null ? Number(item.endereco.longitude) : undefined,
        }
      : undefined,
    perfis_profissionais: (item.perfis_profissionais ?? []).map(
      (p): PerfilProfissional => ({
        id: String(p.id),
        instituicao: p.instituicao,
        cargo: p.cargo,
        tag_id: p.tag_id != null ? String(p.tag_id) : '',
      }),
    ),
    tag_ids: (item.tag_ids ?? []).map(id => String(id)),
    observacoes: item.observacoes || undefined,
    createdAt: item.created_at ?? '',
    updatedAt: item.updated_at ?? '',
    rastreabilidade: mapRastreabilidade(item.rastreabilidade),
  }
}

export interface FetchCidadaosFiltros {
  search?: string
  tagId?: string | null
}

function mapCidadaoToApi(data: Partial<Cidadao>) {
  return {
    nome: data.nome,
    nome_social: data.nome_social ?? '',
    cpf: data.cpf ?? null,
    telefone: data.telefone,
    email: data.email ?? '',
    avatar: data.avatar ?? '',
    observacoes: data.observacoes ?? '',
    bairro: data.bairro ?? data.endereco?.bairro ?? '',
    endereco: data.endereco
      ? {
          ...data.endereco,
          latitude: arredondarCoordenada(data.endereco.latitude),
          longitude: arredondarCoordenada(data.endereco.longitude),
        }
      : null,
    perfis_profissionais: (data.perfis_profissionais ?? []).map(p => ({
      instituicao: p.instituicao,
      cargo: p.cargo,
      tag_id: p.tag_id ? Number(p.tag_id) : null,
    })),
    tag_ids: (data.tag_ids ?? []).map(id => Number(id)),
  }
}

export const useCrmStore = defineStore('crm', () => {
  const cidadaos = ref<Cidadao[]>([])
  const cidadaosTotalCount = ref(0)
  const loading = ref(false)
  const searchQuery = ref('')
  const tagsDisponiveis = ref<Tag[]>([])
  const tagsLoaded = ref(false)

  async function fetchTags() {
    const data = await apiFetch<TagApi[] | DrfPaginated<TagApi>>('/api/crm/tags/')
    const list = Array.isArray(data) ? data : data.results
    tagsDisponiveis.value = list.map(mapTagFromApi)
    tagsLoaded.value = true
  }

  async function ensureTags() {
    if (!tagsLoaded.value) {
      await fetchTags()
    }
  }

  async function fetchCidadaos(
    page = 1,
    perPage = 25,
    filtros?: FetchCidadaosFiltros,
  ): Promise<PaginatedResponse<Cidadao>> {
    loading.value = true
    try {
      await ensureTags()
      const params = new URLSearchParams({
        page: String(page),
        page_size: String(perPage),
      })
      const q = (filtros?.search ?? searchQuery.value).trim()
      if (q) {
        params.set('search', q)
      }
      if (filtros?.tagId) {
        params.set('segmentacao_tag_ids', filtros.tagId)
      }

      const response = await apiFetch<DrfPaginated<CidadaoApi>>(
        `/api/crm/cidadaos/?${params.toString()}`,
      )
      const data = response.results.map(mapCidadaoFromApi)
      cidadaos.value = data
      cidadaosTotalCount.value = response.count

      return {
        data,
        meta: {
          currentPage: page,
          perPage,
          totalPages: Math.max(1, Math.ceil(response.count / perPage)),
          totalItems: response.count,
        },
      }
    } finally {
      loading.value = false
    }
  }

  /** Exportação CSV — percorre páginas na API (não carrega tudo de uma vez). */
  async function iterarCidadaosFiltrados(
    filtros: FetchCidadaosFiltros,
    onPage: (items: Cidadao[]) => void | Promise<void>,
  ): Promise<number> {
    await ensureTags()
    const pageSize = 100
    let page = 1
    let total = 0
    let hasNext = true
    while (hasNext) {
      const params = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize),
      })
      const q = (filtros.search ?? '').trim()
      if (q) {
        params.set('search', q)
      }
      if (filtros.tagId) {
        params.set('segmentacao_tag_ids', filtros.tagId)
      }
      const response = await apiFetch<DrfPaginated<CidadaoApi>>(
        `/api/crm/cidadaos/?${params.toString()}`,
      )
      const batch = response.results.map(mapCidadaoFromApi)
      await onPage(batch)
      total += batch.length
      hasNext = Boolean(response.next)
      page += 1
      if (page > 500) {
        break
      }
    }
    return total
  }

  /** Busca na API (não depende da lista paginada em memória). */
  async function searchCidadaos(
    query: string,
    pageSize = 15,
    options?: { anexoCategoria?: string; curriculoTagIds?: string[] },
  ): Promise<Cidadao[]> {
    const trimmed = query.trim()
    const tagIds = options?.curriculoTagIds?.filter(Boolean) ?? []
    if (!trimmed && !options?.anexoCategoria && tagIds.length === 0) {
      return []
    }
    const params = new URLSearchParams({
      page_size: String(pageSize),
    })
    if (trimmed) {
      params.set('search', trimmed)
    }
    if (options?.anexoCategoria) {
      params.set('anexo_categoria', options.anexoCategoria)
    }
    if (tagIds.length > 0) {
      params.set('curriculo_tag_ids', tagIds.join(','))
      if (!options?.anexoCategoria) {
        params.set('anexo_categoria', 'curriculo')
      }
    }
    const response = await apiFetch<DrfPaginated<CidadaoApi> | CidadaoApi[]>(
      `/api/crm/cidadaos/?${params.toString()}`,
    )
    const list = Array.isArray(response) ? response : (response.results ?? [])
    return list.map(mapCidadaoFromApi)
  }

  /** Contagem de cidadãos com marcador, perfil ou anexo vinculado à(s) tag(s). */
  async function countCidadaosByTagIds(tagIds: string[]): Promise<number> {
    const ids = tagIds.map(id => id.trim()).filter(Boolean)
    if (ids.length === 0) return 0
    const params = new URLSearchParams({
      page_size: '1',
      segmentacao_tag_ids: ids.join(','),
    })
    const response = await apiFetch<DrfPaginated<CidadaoApi>>(
      `/api/crm/cidadaos/?${params.toString()}`,
    )
    return response.count ?? 0
  }

  async function getCidadaoById(id: string, options?: { silent?: boolean }): Promise<Cidadao | null> {
    if (!options?.silent) {
      loading.value = true
    }
    try {
      await ensureTags()
      const data = await apiFetch<CidadaoApi>(`/api/crm/cidadaos/${id}/`)
      const mapped = mapCidadaoFromApi(data)
      const index = cidadaos.value.findIndex(c => c.id === id)
      if (index >= 0) {
        cidadaos.value[index] = mapped
      } else {
        cidadaos.value.push(mapped)
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

  async function createCidadao(data: Partial<Cidadao>): Promise<Cidadao> {
    loading.value = true
    try {
      const created = await apiFetch<CidadaoApi>('/api/crm/cidadaos/', {
        method: 'POST',
        body: JSON.stringify(mapCidadaoToApi(data)),
      })
      const mapped = mapCidadaoFromApi(created)
      cidadaos.value.unshift(mapped)
      cidadaosTotalCount.value += 1
      return mapped
    } finally {
      loading.value = false
    }
  }

  async function updateCidadao(id: string, data: Partial<Cidadao>): Promise<Cidadao | null> {
    loading.value = true
    try {
      const updated = await apiFetch<CidadaoApi>(`/api/crm/cidadaos/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(mapCidadaoToApi(data)),
      })
      const mapped = mapCidadaoFromApi(updated)
      const index = cidadaos.value.findIndex(c => c.id === id)
      if (index >= 0) {
        cidadaos.value[index] = mapped
      }
      return mapped
    } catch {
      return null
    } finally {
      loading.value = false
    }
  }

  async function deleteCidadao(id: string): Promise<boolean> {
    loading.value = true
    try {
      await apiFetch(`/api/crm/cidadaos/${id}/`, {
        method: 'DELETE',
        parseJson: false,
      })
      const index = cidadaos.value.findIndex(c => c.id === id)
      if (index > -1) {
        cidadaos.value.splice(index, 1)
        cidadaosTotalCount.value = Math.max(0, cidadaosTotalCount.value - 1)
      }
      return true
    } catch {
      return false
    } finally {
      loading.value = false
    }
  }

  async function createTag(data: { nome: string; cor: string; modulos: string[]; tipo?: TipoTag }) {
    loading.value = true
    try {
      const modulos =
        data.modulos?.length ? data.modulos : (['crm'] as Tag['modulos'])
      const created = await apiFetch<TagApi>('/api/crm/tags/', {
        method: 'POST',
        body: JSON.stringify({
          nome: data.nome,
          cor: data.cor,
          tipo: data.tipo ?? 'segmentacao',
          modulos,
        }),
      })
      const mapped = mapTagFromApi(created)
      tagsDisponiveis.value.push(mapped)
      return mapped
    } finally {
      loading.value = false
    }
  }

  async function updateTag(id: string, data: { nome: string; cor: string; modulos: string[]; tipo?: TipoTag }) {
    loading.value = true
    try {
      const modulos =
        data.modulos?.length ? data.modulos : (['crm'] as Tag['modulos'])
      const updated = await apiFetch<TagApi>(`/api/crm/tags/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify({
          nome: data.nome,
          cor: data.cor,
          tipo: data.tipo ?? 'segmentacao',
          modulos,
        }),
      })
      const mapped = mapTagFromApi(updated)
      const tag = tagsDisponiveis.value.find(t => t.id === id)
      if (tag) {
        tag.nome = mapped.nome
        tag.cor = mapped.cor
        tag.tipo = mapped.tipo
        tag.modulos = mapped.modulos
      }
      return true
    } finally {
      loading.value = false
    }
  }

  async function deleteTag(id: string) {
    loading.value = true
    try {
      await apiFetch(`/api/crm/tags/${id}/`, {
        method: 'DELETE',
        parseJson: false,
      })
      const index = tagsDisponiveis.value.findIndex(t => t.id === id)
      if (index > -1) {
        tagsDisponiveis.value.splice(index, 1)
      }
      return true
    } catch {
      return false
    } finally {
      loading.value = false
    }
  }

  const tagsPorModulo = (modulo: ModuloTag) => {
    return tagsDisponiveis.value.filter(tag => tag.modulos?.includes(modulo))
  }

  /** Vagas, cursos e currículos (módulo Serviços). */
  const tagsContextoProfissional = computed(() =>
    tagsPorModulo('crm').filter(t => t.tipo === 'contexto_profissional'),
  )

  /** Assistência social — marcadores do cidadão (módulo Serviços). */
  const tagsSegmentacaoServicos = computed(() =>
    tagsPorModulo('crm').filter(t => t.tipo === 'segmentacao' || t.tipo === 'ambos'),
  )

  const tagsParaMarcadores = () =>
    tagsPorModulo('crm').filter(t => t.tipo === 'segmentacao' || t.tipo === 'ambos')

  const tagsParaPerfil = () =>
    tagsPorModulo('crm').filter(t => t.tipo === 'contexto' || t.tipo === 'ambos')

  /** Mailing / cerimonial: todas as tags CRM (marcadores, perfil e currículo). */
  const tagsParaComunicacao = () => tagsPorModulo('crm')

  async function fetchDocumentosCidadao(cidadaoId: string): Promise<CidadaoDocumento[]> {
    const data = await apiFetch<DocumentoAnexoApi[] | DrfPaginated<DocumentoAnexoApi>>(
      `/api/crm/documentos/?cidadao=${encodeURIComponent(cidadaoId)}`,
    )
    const list = Array.isArray(data) ? data : data.results
    return list.map(mapDocumentoFromApi)
  }

  async function uploadDocumentoCidadao(
    cidadaoId: string,
    file: File,
    categoria: CategoriaDocumentoCidadao,
    etiquetaIds: string[] = [],
  ): Promise<CidadaoDocumento> {
    const form = new FormData()
    form.append('cidadao', cidadaoId)
    form.append('categoria', categoria)
    form.append('arquivo', file)
    for (const tagId of etiquetaIds) {
      form.append('etiqueta_ids', tagId)
    }
    const created = await apiUpload<DocumentoAnexoApi>('/api/crm/documentos/', form)
    return mapDocumentoFromApi(created)
  }

  async function updateDocumentoCategoria(
    documentoId: string,
    categoria: CategoriaDocumentoCidadao,
  ): Promise<CidadaoDocumento> {
    const updated = await apiFetch<DocumentoAnexoApi>(`/api/crm/documentos/${documentoId}/`, {
      method: 'PATCH',
      body: JSON.stringify({ categoria }),
    })
    return mapDocumentoFromApi(updated)
  }

  async function updateDocumentoEtiquetas(
    documentoId: string,
    etiquetaIds: string[],
  ): Promise<CidadaoDocumento> {
    const updated = await apiFetch<DocumentoAnexoApi>(`/api/crm/documentos/${documentoId}/`, {
      method: 'PATCH',
      body: JSON.stringify({
        etiqueta_ids: etiquetaIds.map(id => Number(id)),
      }),
    })
    return mapDocumentoFromApi(updated)
  }

  async function deleteDocumentoCidadao(documentoId: string): Promise<void> {
    await apiFetch(`/api/crm/documentos/${documentoId}/`, {
      method: 'DELETE',
      parseJson: false,
    })
  }

  async function downloadDocumentoCidadao(documento: CidadaoDocumento): Promise<void> {
    const path = documento.urlDownload.startsWith('http')
      ? documento.urlDownload
      : documento.urlDownload.replace(/^\//, '')
    const blob = await apiDownload(path)
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = documento.nome
    anchor.click()
    URL.revokeObjectURL(url)
  }

  function cidadaoTemTag(cidadao: Cidadao, tagId: string): boolean {
    if (cidadao.tag_ids?.includes(tagId)) {
      return true
    }
    return cidadao.perfis_profissionais?.some(p => p.tag_id === tagId) ?? false
  }

  return {
    cidadaos,
    cidadaosTotalCount,
    loading,
    searchQuery,
    tagsDisponiveis,
    fetchTags,
    fetchCidadaos,
    iterarCidadaosFiltrados,
    searchCidadaos,
    countCidadaosByTagIds,
    getCidadaoById,
    createCidadao,
    updateCidadao,
    deleteCidadao,
    createTag,
    updateTag,
    deleteTag,
    tagsPorModulo,
    tagsParaMarcadores,
    tagsParaPerfil,
    tagsParaComunicacao,
    cidadaoTemTag,
    fetchDocumentosCidadao,
    uploadDocumentoCidadao,
    updateDocumentoCategoria,
    updateDocumentoEtiquetas,
    tagsContextoProfissional,
    tagsSegmentacaoServicos,
    deleteDocumentoCidadao,
    downloadDocumentoCidadao,
  }
})
