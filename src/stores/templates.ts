import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { TipoDocumento } from '@/types'
import { ApiError, apiFetch } from '@/services/api'

export interface Template {
  id: string
  nome: string
  tipo: TipoDocumento
  conteudo: string
  isDefault: boolean
  descricao?: string
  createdAt: string
  updatedAt?: string
}

interface TemplateDocumentoApi {
  id: number
  nome: string
  tipo_documento: { slug: string }
  descricao?: string
  conteudo: string
  isDefault: boolean
  createdAt: string
  updatedAt?: string
}

function mapTemplateFromApi(item: TemplateDocumentoApi): Template {
  return {
    id: String(item.id),
    nome: item.nome,
    tipo: item.tipo_documento.slug as TipoDocumento,
    conteudo: item.conteudo,
    isDefault: item.isDefault,
    descricao: item.descricao,
    createdAt: item.createdAt,
    updatedAt: item.updatedAt,
  }
}

function getApiErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    const data = error.data
    if (typeof data === 'object' && data !== null) {
      const record = data as Record<string, unknown>
      if (record.detail) return String(record.detail)
    }
    return error.message
  }
  return error instanceof Error ? error.message : 'Erro desconhecido'
}

export const useTemplatesStore = defineStore('templates', () => {
  const templates = ref<Template[]>([])
  const loading = ref(false)

  async function fetchTemplates(tipo?: TipoDocumento) {
    loading.value = true
    try {
      const qs = tipo ? `?tipo=${encodeURIComponent(tipo)}` : ''
      const data = await apiFetch<TemplateDocumentoApi[]>(`/api/documentos/templates${qs}`)
      templates.value = data.map(mapTemplateFromApi)
      return templates.value
    } finally {
      loading.value = false
    }
  }

  async function initialize() {
    if (templates.value.length === 0) {
      await fetchTemplates()
    }
  }

  function getTemplatesByTipo(tipo: TipoDocumento) {
    return templates.value.filter(t => t.tipo === tipo)
  }

  function getDefaultTemplate(tipo: TipoDocumento) {
    return templates.value.find(t => t.tipo === tipo && t.isDefault)
  }

  function getTemplateById(id: string) {
    return templates.value.find(t => t.id === id)
  }

  async function createTemplate(data: Omit<Template, 'id' | 'createdAt'>) {
    loading.value = true
    try {
      const created = await apiFetch<TemplateDocumentoApi>('/api/documentos/templates/', {
        method: 'POST',
        body: JSON.stringify({
          nome: data.nome,
          tipo: data.tipo,
          descricao: data.descricao ?? '',
          conteudo: data.conteudo,
          isDefault: data.isDefault,
        }),
      })
      const mapped = mapTemplateFromApi(created)
      if (mapped.isDefault) {
        templates.value.forEach(t => {
          if (t.tipo === mapped.tipo && t.id !== mapped.id) t.isDefault = false
        })
      }
      templates.value.push(mapped)
      return mapped
    } catch (error) {
      throw new Error(getApiErrorMessage(error))
    } finally {
      loading.value = false
    }
  }

  async function updateTemplate(id: string, data: Partial<Template>) {
    loading.value = true
    try {
      const body: Record<string, unknown> = {}
      if (data.nome !== undefined) body.nome = data.nome
      if (data.tipo !== undefined) body.tipo = data.tipo
      if (data.descricao !== undefined) body.descricao = data.descricao
      if (data.conteudo !== undefined) body.conteudo = data.conteudo
      if (data.isDefault !== undefined) body.isDefault = data.isDefault

      const updated = await apiFetch<TemplateDocumentoApi>(`/api/documentos/templates/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(body),
      })
      const mapped = mapTemplateFromApi(updated)
      const index = templates.value.findIndex(t => t.id === id)
      if (index >= 0) templates.value[index] = mapped
      if (mapped.isDefault) {
        templates.value.forEach(t => {
          if (t.tipo === mapped.tipo && t.id !== mapped.id) t.isDefault = false
        })
      }
      return mapped
    } catch (error) {
      throw new Error(getApiErrorMessage(error))
    } finally {
      loading.value = false
    }
  }

  async function deleteTemplate(id: string) {
    loading.value = true
    try {
      await apiFetch(`/api/documentos/templates/${id}/`, {
        method: 'DELETE',
        parseJson: false,
      })
      templates.value = templates.value.filter(t => t.id !== id)
      return true
    } catch (error) {
      throw new Error(getApiErrorMessage(error))
    } finally {
      loading.value = false
    }
  }

  return {
    templates,
    loading,
    initialize,
    fetchTemplates,
    getTemplatesByTipo,
    getDefaultTemplate,
    getTemplateById,
    createTemplate,
    updateTemplate,
    deleteTemplate,
  }
})
