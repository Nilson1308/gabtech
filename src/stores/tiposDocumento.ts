import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ApiError, apiFetch } from '@/services/api'

export interface TipoDocumentoCustom {
  id: string
  nome: string
  slug: string
  descricao?: string
  icone?: string
  cor?: string
  isSystem: boolean
  createdAt?: string
  updatedAt?: string
}

interface TipoDocumentoApi {
  id: number
  nome: string
  slug: string
  descricao?: string
  icone?: string
  cor?: string
  is_system: boolean
}

function mapTipoFromApi(t: TipoDocumentoApi): TipoDocumentoCustom {
  return {
    id: String(t.id),
    nome: t.nome,
    slug: t.slug,
    descricao: t.descricao,
    icone: t.icone,
    cor: t.cor,
    isSystem: t.is_system,
  }
}

function getApiErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
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
  return error instanceof Error ? error.message : 'Erro desconhecido'
}

export const useTiposDocumentoStore = defineStore('tiposDocumento', () => {
  const tipos = ref<TipoDocumentoCustom[]>([])
  const loading = ref(false)

  async function fetchTipos() {
    loading.value = true
    try {
      const data = await apiFetch<TipoDocumentoApi[]>('/api/documentos/tipos/')
      tipos.value = data.map(mapTipoFromApi)
      return tipos.value
    } finally {
      loading.value = false
    }
  }

  async function initialize() {
    if (tipos.value.length === 0) {
      await fetchTipos()
    }
  }

  function getTipoBySlug(slug: string) {
    return tipos.value.find(t => t.slug === slug)
  }

  function getTipoById(id: string) {
    return tipos.value.find(t => t.id === id)
  }

  async function createTipo(data: Omit<TipoDocumentoCustom, 'id' | 'createdAt' | 'isSystem'>) {
    loading.value = true
    try {
      const body: Record<string, string> = {
        nome: data.nome,
        descricao: data.descricao ?? '',
        icone: data.icone ?? 'file-text',
        cor: data.cor ?? '#3b82f6',
      }
      if (data.slug?.trim()) {
        body.slug = data.slug.trim()
      }
      const created = await apiFetch<TipoDocumentoApi>('/api/documentos/tipos/', {
        method: 'POST',
        body: JSON.stringify(body),
      })
      const mapped = mapTipoFromApi(created)
      tipos.value.push(mapped)
      return mapped
    } catch (error) {
      throw new Error(getApiErrorMessage(error))
    } finally {
      loading.value = false
    }
  }

  async function updateTipo(id: string, data: Partial<TipoDocumentoCustom>) {
    const tipo = tipos.value.find(t => t.id === id)
    if (tipo?.isSystem && data.slug && data.slug !== tipo.slug) {
      throw new Error('Tipos do sistema não podem ter o slug alterado.')
    }

    loading.value = true
    try {
      const updated = await apiFetch<TipoDocumentoApi>(`/api/documentos/tipos/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify({
          nome: data.nome,
          descricao: data.descricao,
          icone: data.icone,
          cor: data.cor,
          ...(data.slug && !tipo?.isSystem ? { slug: data.slug } : {}),
        }),
      })
      const mapped = mapTipoFromApi(updated)
      const index = tipos.value.findIndex(t => t.id === id)
      if (index >= 0) tipos.value[index] = mapped
      return mapped
    } catch (error) {
      throw new Error(getApiErrorMessage(error))
    } finally {
      loading.value = false
    }
  }

  async function deleteTipo(id: string) {
    const tipo = tipos.value.find(t => t.id === id)
    if (tipo?.isSystem) {
      throw new Error('Tipos do sistema não podem ser excluídos')
    }

    loading.value = true
    try {
      await apiFetch(`/api/documentos/tipos/${id}/`, {
        method: 'DELETE',
        parseJson: false,
      })
      tipos.value = tipos.value.filter(t => t.id !== id)
      return true
    } catch (error) {
      throw new Error(getApiErrorMessage(error))
    } finally {
      loading.value = false
    }
  }

  return {
    tipos,
    loading,
    initialize,
    fetchTipos,
    getTipoBySlug,
    getTipoById,
    createTipo,
    updateTipo,
    deleteTipo,
  }
})
