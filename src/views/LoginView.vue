<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { resolveTenantApiBaseUrl, syncTenantApiBaseFromBrowser } from '@/services/api'
import { Mail, Lock, LogIn, AlertCircle, Moon, Sun } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const senha = ref('')
const loading = ref(false)
const erro = ref<string | null>(null)
const darkMode = ref(false)
const apiBaseDev = ref('')
const isDev = import.meta.env.DEV

// Detectar preferência de tema ao montar
onMounted(() => {
  darkMode.value = document.documentElement.classList.contains('dark')
  syncTenantApiBaseFromBrowser()
  if (import.meta.env.DEV) {
    apiBaseDev.value = resolveTenantApiBaseUrl()
  }
})

// Toggle dark mode
const toggleDarkMode = () => {
  darkMode.value = !darkMode.value
  if (darkMode.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

const formularioValido = computed(() => {
  return email.value.includes('@') && senha.value.length > 0
})

const handleSubmit = async () => {
  if (!formularioValido.value) {
    erro.value = 'Por favor, preencha todos os campos corretamente.'
    return
  }

  loading.value = true
  erro.value = null

  try {
    const result = await authStore.login({
      email: email.value,
      senha: senha.value,
    })

    if (result.success) {
      router.push('/dashboard')
    } else {
      erro.value = result.error || 'Erro ao fazer login. Tente novamente.'
    }
  } catch (error) {
    erro.value = 'Erro ao conectar. Tente novamente.'
  } finally {
    loading.value = false
  }
}

</script>

<template>
  <div class="min-h-screen flex bg-gray-50 dark:bg-slate-900 transition-colors duration-300">
    <!-- Lado Esquerdo: Banner Institucional -->
    <div class="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-900 via-primary-800 to-primary-700 dark:from-slate-800 dark:via-slate-900 dark:to-slate-950 p-12 flex-col justify-between relative overflow-hidden">
      <!-- Padrão de fundo decorativo -->
      <div class="absolute inset-0 opacity-10">
        <div class="absolute top-20 right-20 w-96 h-96 bg-white rounded-full blur-3xl"></div>
        <div class="absolute bottom-20 left-20 w-96 h-96 bg-primary-400 rounded-full blur-3xl"></div>
      </div>

      <div class="relative z-10">
        <!-- Logo Completo -->
        <div class="mb-12">
          <img 
            v-if="!darkMode"
            src="/logo_gt_tema_escuro_completo.png" 
            alt="GabTech" 
            class="h-12 w-auto"
          />
          <img 
            v-else
            src="/logo_gt_tema_escuro_completo.png" 
            alt="GabTech" 
            class="h-12 w-auto"
          />
        </div>
        
        <div class="mt-20 space-y-6 max-w-lg">
          <h2 class="text-white text-5xl font-bold leading-tight">
            Gestão de Gabinetes Públicos
          </h2>
          <p class="text-primary-100 dark:text-slate-300 text-lg leading-relaxed">
            Plataforma completa para gestão de gabinetes executivos e legislativos. 
            Gerencie cidadãos, atendimentos, eventos e documentos em um único lugar.
          </p>

          <!-- Features -->
          <div class="mt-12 space-y-4">
            <div class="flex items-center gap-3 text-white">
              <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <span class="text-primary-100 dark:text-slate-300">CRM completo para gestão de cidadãos</span>
            </div>
            <div class="flex items-center gap-3 text-white">
              <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <span class="text-primary-100 dark:text-slate-300">Sistema de atendimentos e protocolos</span>
            </div>
            <div class="flex items-center gap-3 text-white">
              <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <span class="text-primary-100 dark:text-slate-300">Dashboard executivo e inteligência territorial</span>
            </div>
          </div>
        </div>
      </div>

      <div class="text-primary-200 dark:text-slate-400 text-sm relative z-10">
        <p>© 2026 GabTech. Todos os direitos reservados.</p>
      </div>
    </div>

    <!-- Lado Direito: Formulário de Login -->
    <div class="flex-1 flex items-center justify-center p-8 bg-white dark:bg-slate-900 relative">
      <!-- Botão Dark Mode -->
      <button
        @click="toggleDarkMode"
        class="absolute top-6 right-6 p-2 rounded-lg bg-gray-100 dark:bg-slate-800 hover:bg-gray-200 dark:hover:bg-slate-700 transition-colors"
        title="Alternar tema"
      >
        <Sun v-if="darkMode" class="w-5 h-5 text-yellow-500" />
        <Moon v-else class="w-5 h-5 text-gray-700" />
      </button>

      <div class="w-full max-w-md">
        <!-- Logo Mobile -->
        <div class="lg:hidden flex items-center justify-center mb-8">
          <img 
            v-if="!darkMode"
            src="/logo_gt_tema_claro_completo.png" 
            alt="GabTech" 
            class="h-10 w-auto"
          />
          <img 
            v-else
            src="/logo_gt_tema_escuro_completo.png" 
            alt="GabTech" 
            class="h-10 w-auto"
          />
        </div>

        <!-- Cabeçalho -->
        <div class="mb-8 text-center lg:text-left">
          <h2 class="text-3xl font-bold text-gray-900 dark:text-slate-100 mb-2">
            Bem-vindo de volta
          </h2>
          <p class="text-gray-600 dark:text-slate-400">
            Entre com suas credenciais para acessar o sistema
          </p>
        </div>

        <!-- Alerta de Erro -->
        <Transition
          enter-active-class="transition-all duration-300"
          enter-from-class="opacity-0 -translate-y-2"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition-all duration-300"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-2"
        >
          <div
            v-if="erro"
            class="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3"
          >
            <AlertCircle class="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <p class="text-sm text-red-800 dark:text-red-300">{{ erro }}</p>
          </div>
        </Transition>

        <!-- Formulário -->
        <form @submit.prevent="handleSubmit" class="space-y-5">
          <!-- Campo Email -->
          <div>
            <label for="email" class="label">
              E-mail
            </label>
            <div class="relative">
              <Mail class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-slate-500" />
              <input
                id="email"
                v-model="email"
                type="email"
                placeholder="seu.email@exemplo.com"
                class="input pl-10"
                :disabled="loading"
                required
              />
            </div>
          </div>

          <!-- Campo Senha -->
          <div>
            <label for="senha" class="label">
              Senha
            </label>
            <div class="relative">
              <Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-slate-500" />
              <input
                id="senha"
                v-model="senha"
                type="password"
                placeholder="••••••••"
                class="input pl-10"
                :disabled="loading"
                required
              />
            </div>
          </div>

          <!-- Botão de Submit -->
          <button
            type="submit"
            :disabled="loading || !formularioValido"
            class="btn btn-primary w-full text-base py-3 mt-6"
          >
            <div v-if="loading" class="flex items-center justify-center gap-2">
              <div class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Entrando...</span>
            </div>
            <div v-else class="flex items-center justify-center gap-2">
              <LogIn class="w-5 h-5" />
              <span>Entrar</span>
            </div>
          </button>
        </form>

        <p
          v-if="isDev && apiBaseDev"
          class="mt-6 text-center text-xs text-gray-500 dark:text-slate-500 font-mono break-all"
        >
          API: {{ apiBaseDev }}
        </p>

      </div>
    </div>
  </div>
</template>
