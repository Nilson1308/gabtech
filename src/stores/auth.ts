import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Usuario, LoginCredentials } from '@/types'
import { ApiError, apiFetch, getStoredToken } from '@/services/api'
import { permissionGranted } from '@/constants/rbac'

interface LoginApiUser {
  id: number
  nome: string
  email: string
  avatar: string
  cargo: string
  permissions: string[]
}

interface LoginApiResponse {
  token: string
  user: LoginApiUser
}

const STORAGE_USER = 'usuario'
const STORAGE_TOKEN = 'token'

function defaultAvatar(nome: string): string {
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(nome)}&background=3b82f6&color=fff`
}

function mapApiUserToUsuario(apiUser: LoginApiUser): Usuario {
  return {
    id: String(apiUser.id),
    nome: apiUser.nome,
    email: apiUser.email,
    avatar: apiUser.avatar || defaultAvatar(apiUser.nome),
    cargo: apiUser.cargo,
    tenantId: apiUser.email.split('@')[1] || 'demo.localhost',
    permissions: apiUser.permissions ?? [],
    createdAt: new Date().toISOString(),
  }
}

function persistSession(accessToken: string, user: Usuario) {
  localStorage.setItem(STORAGE_TOKEN, accessToken)
  localStorage.setItem(STORAGE_USER, JSON.stringify(user))
}

export const useAuthStore = defineStore('auth', () => {
  const usuario = ref<Usuario | null>(null)
  const token = ref<string | null>(getStoredToken())

  const user = computed(() => usuario.value)
  const permissions = computed(() => usuario.value?.permissions ?? [])

  const isAuthenticated = computed(() => !!token.value && !!usuario.value)

  const hasPermission = computed(() => (permission: string) => {
    if (usuario.value?.cargo === 'Administrador') {
      return true
    }
    const perms = usuario.value?.permissions ?? []
    return permissionGranted(perms, permission)
  })

  async function login(credentials: LoginCredentials) {
    try {
      const data = await apiFetch<LoginApiResponse>('/api/auth/login/', {
        method: 'POST',
        skipAuth: true,
        body: JSON.stringify({
          email: credentials.email.trim(),
          senha: credentials.senha,
        }),
      })

      const mappedUser = mapApiUserToUsuario(data.user)

      token.value = data.token
      usuario.value = mappedUser
      persistSession(data.token, mappedUser)

      return { success: true as const }
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : error instanceof Error && error.message
            ? error.message
            : 'Credenciais inválidas'
      return { success: false as const, error: message }
    }
  }

  function logout() {
    usuario.value = null
    token.value = null
    localStorage.removeItem(STORAGE_TOKEN)
    localStorage.removeItem(STORAGE_USER)
  }

  function loadUserFromStorage() {
    const storedToken = localStorage.getItem(STORAGE_TOKEN)
    const storedUser = localStorage.getItem(STORAGE_USER)

    if (storedToken && storedUser) {
      try {
        token.value = storedToken
        usuario.value = JSON.parse(storedUser) as Usuario
      } catch {
        logout()
      }
    }
  }

  loadUserFromStorage()

  return {
    usuario,
    user,
    permissions,
    token,
    isAuthenticated,
    hasPermission,
    login,
    logout,
    loadUserFromStorage,
  }
})
