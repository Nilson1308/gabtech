import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Documento,
  PastaDocumento,
  EtiquetaDocumento,
  TipoDocumento,
  StatusDocumento,
  Usuario,
  VersaoDocumento,
} from '@/types'
import { ApiError, apiFetch, apiUpload } from '@/services/api'
import { mapRastreabilidade, type RastreabilidadeApi } from '@/utils/rastreabilidade'

interface UsuarioApi {
  id: number
  nome: string
  email: string
  avatar?: string
  cargo: string
  permissions?: string[]
}

interface PastaDocumentoApi {
  id: number
  nome: string
  icone?: string
  cor?: string
  parentId?: string | null
  created_at: string
}

interface TipoDocumentoApi {
  id: number
  slug: string
  nome: string
  icone?: string
  cor?: string
}

interface EtiquetaDocumentoApi {
  id: number
  nome: string
  cor: string
  created_at: string
}

interface VersaoDocumentoApi {
  id: number
  documento_id: number
  numero_versao: number
  autor: UsuarioApi | null
  conteudo: string
  mudancas?: string
  created_at: string
}

interface DocumentoApi {
  id: number
  titulo: string
  tipo_documento: TipoDocumentoApi
  pasta?: PastaDocumentoApi | null
  conteudo: string
  autor: UsuarioApi
  status: StatusDocumento
  versao_atual: number
  assinantes?: UsuarioApi[]
  etiquetas?: EtiquetaDocumentoApi[]
  versoes?: VersaoDocumentoApi[]
  created_at: string
  updated_at: string
  finalizado_at?: string | null
  rastreabilidade?: RastreabilidadeApi
}

interface DrfPaginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

function defaultAvatar(nome: string): string {
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(nome)}&background=3b82f6&color=fff`
}

function mapUsuario(u: UsuarioApi): Usuario {
  return {
    id: String(u.id),
    nome: u.nome,
    email: u.email,
    avatar: u.avatar || defaultAvatar(u.nome),
    cargo: u.cargo,
    tenantId: u.email.split('@')[1] || 'demo.localhost',
    permissions: u.permissions ?? [],
    createdAt: new Date().toISOString(),
  }
}

function mapEtiquetaFromApi(e: EtiquetaDocumentoApi): EtiquetaDocumento {
  return {
    id: String(e.id),
    nome: e.nome,
    cor: e.cor,
  }
}

function mapPastaFromApi(p: PastaDocumentoApi): PastaDocumento {
  return {
    id: String(p.id),
    nome: p.nome,
    icone: p.icone,
    cor: p.cor,
    parentId: p.parentId ?? undefined,
    createdAt: p.created_at,
  }
}

function mapVersaoFromApi(v: VersaoDocumentoApi): VersaoDocumento {
  return {
    id: String(v.id),
    documentoId: String(v.documento_id),
    numeroVersao: v.numero_versao,
    autorId: v.autor ? String(v.autor.id) : '',
    autor: v.autor ? mapUsuario(v.autor) : mapUsuario({ id: 0, nome: '—', email: '', cargo: '—' }),
    mudancas: v.mudancas || 'Alteração de conteúdo',
    conteudo: v.conteudo,
    createdAt: v.created_at,
  }
}

function mapDocumentoFromApi(item: DocumentoApi): Documento {
  return {
    id: String(item.id),
    titulo: item.titulo,
    tipo: item.tipo_documento.slug as TipoDocumento,
    status: item.status,
    pastaId: item.pasta ? String(item.pasta.id) : undefined,
    pasta: item.pasta ? mapPastaFromApi(item.pasta) : undefined,
    conteudo: item.conteudo,
    autorId: String(item.autor.id),
    autor: mapUsuario(item.autor),
    assinantes: (item.assinantes ?? []).map(mapUsuario),
    etiquetas: (item.etiquetas ?? []).map(mapEtiquetaFromApi),
    versoes: (item.versoes ?? []).map(mapVersaoFromApi),
    versaoAtual: item.versao_atual,
    createdAt: item.created_at,
    updatedAt: item.updated_at,
    finalizadoAt: item.finalizado_at ?? undefined,
    rastreabilidade: mapRastreabilidade(item.rastreabilidade),
  }
}

export function getDocumentosApiErrorMessage(error: unknown): string {
  if (!(error instanceof ApiError)) {
    return error instanceof Error ? error.message : 'Erro desconhecido'
  }
  const data = error.data
  if (typeof data === 'object' && data !== null) {
    const record = data as Record<string, unknown>
    if (record.detail) return String(record.detail)
    const first = Object.values(record)[0]
    if (Array.isArray(first) && first.length) return String(first[0])
    if (typeof first === 'string') return first
  }
  return error.message
}

async function fetchAllDocumentos(): Promise<DocumentoApi[]> {
  const data = await apiFetch<DocumentoApi[] | DrfPaginated<DocumentoApi>>(
    '/api/documentos/documentos/',
  )
  if (Array.isArray(data)) {
    return data
  }
  const aggregated = [...data.results]
  let next = data.next
  let page = 2
  while (next && page <= 50) {
    const response = await apiFetch<DrfPaginated<DocumentoApi>>(
      `/api/documentos/documentos/?page=${page}&page_size=200`,
    )
    aggregated.push(...response.results)
    next = response.next
    page += 1
  }
  return aggregated
}

export const useDocumentosStore = defineStore('documentos', () => {
  const documentos = ref<Documento[]>([])
  const pastas = ref<PastaDocumento[]>([])
  const etiquetas = ref<EtiquetaDocumento[]>([])
  const loading = ref(false)
  const pastaAtiva = ref<string | null>(null)
  const etiquetaAtiva = ref<string | null>(null)
  const filtroStatus = ref<StatusDocumento | null>(null)

  const documentosFiltrados = computed(() => {
    let docs = documentos.value

    if (pastaAtiva.value && pastaAtiva.value !== 'sem-pasta') {
      docs = docs.filter(d => d.pastaId === pastaAtiva.value)
    }

    if (etiquetaAtiva.value) {
      docs = docs.filter(d => d.etiquetas.some(e => e.id === etiquetaAtiva.value))
    }

    if (filtroStatus.value) {
      docs = docs.filter(d => d.status === filtroStatus.value)
    }

    return docs.sort(
      (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime(),
    )
  })

  const documentosPorStatus = computed(() => ({
    rascunho: documentos.value.filter(d => d.status === 'rascunho').length,
    aguardando_assinatura: documentos.value.filter(d => d.status === 'aguardando_assinatura').length,
    finalizado: documentos.value.filter(d => d.status === 'finalizado').length,
  }))

  async function fetchPastas() {
    const data = await apiFetch<PastaDocumentoApi[]>('/api/documentos/pastas/')
    pastas.value = data.map(mapPastaFromApi)
    return pastas.value
  }

  async function fetchEtiquetas() {
    const data = await apiFetch<EtiquetaDocumentoApi[]>('/api/documentos/etiquetas/')
    etiquetas.value = data.map(mapEtiquetaFromApi)
    return etiquetas.value
  }

  async function fetchDocumentos() {
    const list = await fetchAllDocumentos()
    documentos.value = list.map(mapDocumentoFromApi)
    return documentos.value
  }

  async function initialize() {
    loading.value = true
    try {
      await Promise.all([fetchPastas(), fetchEtiquetas(), fetchDocumentos()])
    } finally {
      loading.value = false
    }
  }

  async function fetchDocumentoById(id: string): Promise<Documento | undefined> {
    const existing = documentos.value.find(d => d.id === id)
    if (existing) return existing

    try {
      const item = await apiFetch<DocumentoApi>(`/api/documentos/documentos/${id}/`)
      const mapped = mapDocumentoFromApi(item)
      const index = documentos.value.findIndex(d => d.id === id)
      if (index >= 0) {
        documentos.value[index] = mapped
      } else {
        documentos.value.push(mapped)
      }
      return mapped
    } catch {
      return undefined
    }
  }

  function getDocumentoById(id: string): Documento | undefined {
    return documentos.value.find(d => d.id === id)
  }

  async function resolveTipoDocumentoId(slug: TipoDocumento): Promise<number> {
    const tipos = await apiFetch<TipoDocumentoApi[]>('/api/documentos/tipos/')
    const tipo = tipos.find(t => t.slug === slug)
    if (!tipo) throw new Error(`Tipo de documento «${slug}» não encontrado.`)
    return tipo.id
  }

  async function createDocumento(data: {
    titulo: string
    tipo: TipoDocumento
    pastaId?: string
    conteudo?: string
    etiquetaIds?: string[]
  }) {
    loading.value = true
    try {
      const tipoId = await resolveTipoDocumentoId(data.tipo)
      const created = await apiFetch<DocumentoApi>('/api/documentos/documentos/', {
        method: 'POST',
        body: JSON.stringify({
          titulo: data.titulo,
          tipo_documento_id: tipoId,
          pasta_id: data.pastaId ? Number(data.pastaId) : null,
          conteudo: data.conteudo ?? '<p>Conteúdo do documento...</p>',
          status: 'rascunho',
          etiqueta_ids: (data.etiquetaIds ?? []).map(id => Number(id)),
        }),
      })
      const mapped = mapDocumentoFromApi(created)
      documentos.value.unshift(mapped)
      return mapped
    } catch (error) {
      throw new Error(getDocumentosApiErrorMessage(error))
    } finally {
      loading.value = false
    }
  }

  async function updateDocumento(
    id: string,
    data: Partial<Documento> & { etiquetaIds?: string[] },
  ) {
    loading.value = true
    try {
      const payload: Record<string, unknown> = {}
      if (data.titulo !== undefined) payload.titulo = data.titulo
      if (data.conteudo !== undefined) payload.conteudo = data.conteudo
      if (data.status !== undefined) payload.status = data.status
      if (data.pastaId !== undefined) {
        payload.pasta_id = data.pastaId ? Number(data.pastaId) : null
      }
      if (data.etiquetaIds !== undefined) {
        payload.etiqueta_ids = data.etiquetaIds.map(eid => Number(eid))
      }

      const updated = await apiFetch<DocumentoApi>(`/api/documentos/documentos/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      })
      const mapped = mapDocumentoFromApi(updated)
      const index = documentos.value.findIndex(d => d.id === id)
      if (index >= 0) documentos.value[index] = mapped
      return mapped
    } catch (error) {
      throw new Error(getDocumentosApiErrorMessage(error))
    } finally {
      loading.value = false
    }
  }

  async function changeStatus(id: string, novoStatus: StatusDocumento) {
    return updateDocumento(id, { status: novoStatus })
  }

  async function restaurarVersao(documentoId: string, numeroVersao: number) {
    loading.value = true
    try {
      const updated = await apiFetch<DocumentoApi>(
        `/api/documentos/documentos/${documentoId}/restaurar-versao/`,
        {
          method: 'POST',
          body: JSON.stringify({ numero_versao: numeroVersao }),
        },
      )
      const mapped = mapDocumentoFromApi(updated)
      const index = documentos.value.findIndex(d => d.id === documentoId)
      if (index >= 0) documentos.value[index] = mapped
      return mapped
    } catch (error) {
      throw new Error(getDocumentosApiErrorMessage(error))
    } finally {
      loading.value = false
    }
  }

  async function deleteDocumento(id: string) {
    loading.value = true
    try {
      await apiFetch(`/api/documentos/documentos/${id}/`, {
        method: 'DELETE',
        parseJson: false,
      })
      documentos.value = documentos.value.filter(d => d.id !== id)
      return true
    } catch (error) {
      throw new Error(getDocumentosApiErrorMessage(error))
    } finally {
      loading.value = false
    }
  }

  async function createPasta(data: {
    nome: string
    icone?: string
    cor?: string
    parentId?: string
  }) {
    loading.value = true
    try {
      const created = await apiFetch<PastaDocumentoApi>('/api/documentos/pastas/', {
        method: 'POST',
        body: JSON.stringify({
          nome: data.nome,
          icone: data.icone ?? 'folder',
          cor: data.cor ?? '#3b82f6',
          parent_id: data.parentId ? Number(data.parentId) : null,
        }),
      })
      const mapped = mapPastaFromApi(created)
      pastas.value.push(mapped)
      return mapped
    } catch (error) {
      throw new Error(getDocumentosApiErrorMessage(error))
    } finally {
      loading.value = false
    }
  }

  async function updatePasta(id: string, data: Partial<PastaDocumento>) {
    loading.value = true
    try {
      const updated = await apiFetch<PastaDocumentoApi>(`/api/documentos/pastas/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify({
          nome: data.nome,
          icone: data.icone,
          cor: data.cor,
          parent_id: data.parentId ? Number(data.parentId) : null,
        }),
      })
      const mapped = mapPastaFromApi(updated)
      const index = pastas.value.findIndex(p => p.id === id)
      if (index >= 0) pastas.value[index] = mapped
      return mapped
    } catch (error) {
      throw new Error(getDocumentosApiErrorMessage(error))
    } finally {
      loading.value = false
    }
  }

  async function deletePasta(id: string) {
    loading.value = true
    try {
      await apiFetch(`/api/documentos/pastas/${id}/`, {
        method: 'DELETE',
        parseJson: false,
      })
      pastas.value = pastas.value.filter(p => p.id !== id)
      return true
    } catch (error) {
      throw new Error(getDocumentosApiErrorMessage(error))
    } finally {
      loading.value = false
    }
  }

  async function moverParaPasta(documentoId: string, pastaId: string | null) {
    return updateDocumento(documentoId, { pastaId: pastaId ?? undefined })
  }

  function setPastaAtiva(pastaId: string | null) {
    pastaAtiva.value = pastaId
  }

  function setFiltroStatus(status: StatusDocumento | null) {
    filtroStatus.value = status
  }

  function setEtiquetaAtiva(etiquetaId: string | null) {
    etiquetaAtiva.value = etiquetaId
  }

  function contarDocumentosPorEtiqueta(etiquetaId: string): number {
    return documentos.value.filter(d => d.etiquetas.some(e => e.id === etiquetaId)).length
  }

  async function createEtiqueta(data: { nome: string; cor?: string }) {
    const created = await apiFetch<EtiquetaDocumentoApi>('/api/documentos/etiquetas/', {
      method: 'POST',
      body: JSON.stringify({
        nome: data.nome,
        cor: data.cor ?? '#6b7280',
      }),
    })
    const mapped = mapEtiquetaFromApi(created)
    etiquetas.value.push(mapped)
    etiquetas.value.sort((a, b) => a.nome.localeCompare(b.nome))
    return mapped
  }

  async function updateEtiqueta(id: string, data: Partial<EtiquetaDocumento>) {
    const updated = await apiFetch<EtiquetaDocumentoApi>(`/api/documentos/etiquetas/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify({
        nome: data.nome,
        cor: data.cor,
      }),
    })
    const mapped = mapEtiquetaFromApi(updated)
    const index = etiquetas.value.findIndex(e => e.id === id)
    if (index >= 0) etiquetas.value[index] = mapped
    documentos.value.forEach(doc => {
      doc.etiquetas = doc.etiquetas.map(e => (e.id === id ? mapped : e))
    })
    return mapped
  }

  async function deleteEtiqueta(id: string) {
    try {
      await apiFetch(`/api/documentos/etiquetas/${id}/`, {
        method: 'DELETE',
        parseJson: false,
      })
      etiquetas.value = etiquetas.value.filter(e => e.id !== id)
      documentos.value.forEach(doc => {
        doc.etiquetas = doc.etiquetas.filter(e => e.id !== id)
      })
      if (etiquetaAtiva.value === id) etiquetaAtiva.value = null
      return true
    } catch (error) {
      throw new Error(getDocumentosApiErrorMessage(error))
    }
  }

  async function fetchMinhaAssinaturaVisual(): Promise<string | null> {
    const data = await apiFetch<{ url: string | null; has_assinatura: boolean }>(
      '/api/documentos/minha-assinatura/',
    )
    return data.url ?? null
  }

  async function uploadMinhaAssinaturaVisual(dataUrl: string): Promise<string> {
    const response = await fetch(dataUrl)
    const blob = await response.blob()
    const form = new FormData()
    const mime = blob.type || 'image/png'
    const ext = mime === 'image/jpeg' ? 'jpg' : mime === 'image/webp' ? 'webp' : 'png'
    form.append('arquivo', blob, `assinatura.${ext}`)

    const data = await apiUpload<{ url: string }>('/api/documentos/minha-assinatura/', form)
    if (!data.url) {
      throw new Error('Resposta inválida ao salvar assinatura.')
    }
    return data.url
  }

  async function removerMinhaAssinaturaVisual() {
    await apiFetch('/api/documentos/minha-assinatura/', {
      method: 'DELETE',
      parseJson: false,
    })
  }

  return {
    documentos,
    pastas,
    etiquetas,
    loading,
    pastaAtiva,
    etiquetaAtiva,
    filtroStatus,
    documentosFiltrados,
    documentosPorStatus,
    initialize,
    fetchPastas,
    fetchEtiquetas,
    fetchDocumentos,
    fetchDocumentoById,
    getDocumentoById,
    createDocumento,
    updateDocumento,
    changeStatus,
    restaurarVersao,
    deleteDocumento,
    moverParaPasta,
    setPastaAtiva,
    setEtiquetaAtiva,
    setFiltroStatus,
    contarDocumentosPorEtiqueta,
    createEtiqueta,
    updateEtiqueta,
    deleteEtiqueta,
    createPasta,
    updatePasta,
    deletePasta,
    getDocumentosApiErrorMessage,
    fetchMinhaAssinaturaVisual,
    uploadMinhaAssinaturaVisual,
    removerMinhaAssinaturaVisual,
  }
})
