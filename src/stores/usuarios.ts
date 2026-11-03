import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ApiError, apiFetch } from '@/services/api'
import { mapRastreabilidade, type RastreabilidadeApi } from '@/utils/rastreabilidade'

export interface Usuario {
  id: string
  nome: string
  email: string
  avatar?: string
  perfilId: string
  perfilNome: string
  perfilCor: string
  cargo: string
  status: 'ativo' | 'inativo'
  createdAt: string
  updatedAt: string
  rastreabilidade?: import('@/utils/rastreabilidade').Rastreabilidade | null
}

interface PerfilBasicoApi {
  id: number
  nome: string
  cor: string
  is_admin: boolean
}

interface UsuarioApi {
  id: number
  nome: string
  email: string
  avatar?: string
  cargo: string
  status: 'ativo' | 'inativo'
  perfil: PerfilBasicoApi | null
  created_at: string
  updated_at: string | null
  rastreabilidade?: RastreabilidadeApi
}

function mapUsuarioFromApi(item: UsuarioApi): Usuario {
  return {
    id: String(item.id),
    nome: item.nome,
    email: item.email,
    avatar: item.avatar || '',
    perfilId: item.perfil ? String(item.perfil.id) : '',
    perfilNome: item.perfil?.nome ?? item.cargo ?? '',
    perfilCor: item.perfil?.cor ?? '#6b7280',
    cargo: item.cargo || item.perfil?.nome || '',
    status: item.status,
    createdAt: item.created_at,
    updatedAt: item.updated_at ?? item.created_at,
    rastreabilidade: mapRastreabilidade(item.rastreabilidade),
  }
}

function buildUsuarioPayload(data: {
  nome: string
  email: string
  perfilId: string
  status: 'ativo' | 'inativo'
  senha?: string
}) {
  const payload: Record<string, unknown> = {
    nome: data.nome.trim(),
    email: data.email.trim().toLowerCase(),
    perfil_id: Number(data.perfilId),
    status: data.status,
  }
  if (data.senha?.trim()) {
    payload.password = data.senha
  }
  return payload
}

export const useUsuariosStore = defineStore('usuarios', () => {
  const usuarios = ref<Usuario[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchUsuarios() {
    loading.value = true
    error.value = null
    try {
      const data = await apiFetch<UsuarioApi[]>('/api/usuarios/')
      usuarios.value = data.map(mapUsuarioFromApi)
    } catch (err) {
      error.value = err instanceof ApiError ? err.message : 'Erro ao carregar usuários'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function initialize() {
    await fetchUsuarios()
  }

  async function createUsuario(data: {
    nome: string
    email: string
    perfilId: string
    status: 'ativo' | 'inativo'
    senha?: string
  }) {
    loading.value = true
    error.value = null
    try {
      const created = await apiFetch<UsuarioApi>('/api/usuarios/', {
        method: 'POST',
        body: JSON.stringify(buildUsuarioPayload({ ...data, senha: data.senha })),
      })
      const mapped = mapUsuarioFromApi(created)
      usuarios.value.push(mapped)
      return mapped
    } catch (err) {
      error.value = err instanceof ApiError ? err.message : 'Erro ao criar usuário'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateUsuario(
    id: string,
    data: Partial<{
      nome: string
      email: string
      perfilId: string
      status: 'ativo' | 'inativo'
      senha: string
    }>,
  ) {
    loading.value = true
    error.value = null
    try {
      const payload: Record<string, unknown> = {}
      if (data.nome !== undefined) payload.nome = data.nome.trim()
      if (data.email !== undefined) payload.email = data.email.trim().toLowerCase()
      if (data.perfilId !== undefined) payload.perfil_id = Number(data.perfilId)
      if (data.status !== undefined) payload.status = data.status
      if (data.senha?.trim()) payload.password = data.senha

      const updated = await apiFetch<UsuarioApi>(`/api/usuarios/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      })
      const mapped = mapUsuarioFromApi(updated)
      const index = usuarios.value.findIndex(u => u.id === id)
      if (index > -1) {
        usuarios.value[index] = mapped
      }
      return mapped
    } catch (err) {
      error.value = err instanceof ApiError ? err.message : 'Erro ao atualizar usuário'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function inativarUsuario(id: string) {
    return updateUsuario(id, { status: 'inativo' })
  }

  async function deleteUsuario(id: string) {
    loading.value = true
    error.value = null
    try {
      await apiFetch(`/api/usuarios/${id}/`, {
        method: 'DELETE',
        parseJson: false,
      })
      const usuario = usuarios.value.find(u => u.id === id)
      if (usuario) {
        usuario.status = 'inativo'
      }
    } catch (err) {
      error.value = err instanceof ApiError ? err.message : 'Erro ao inativar usuário'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function toggleStatus(id: string) {
    const usuario = usuarios.value.find(u => u.id === id)
    if (!usuario) return
    const novoStatus = usuario.status === 'ativo' ? 'inativo' : 'ativo'
    await updateUsuario(id, { status: novoStatus })
  }

  return {
    usuarios,
    loading,
    error,
    initialize,
    fetchUsuarios,
    createUsuario,
    updateUsuario,
    inativarUsuario,
    deleteUsuario,
    toggleStatus,
  }
})
