<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { CheckCircle, Loader2, XCircle, ExternalLink } from 'lucide-vue-next'
import { consultarCadastroGabinete, type CadastroGabineteResposta } from '@/services/platform'
import { setTenantApiBaseUrl } from '@/services/api'

const route = useRoute()
const cadastro = ref<CadastroGabineteResposta | null>(null)
const erro = ref<string | null>(null)
let timer: ReturnType<typeof setInterval> | null = null

async function carregar() {
  const id = route.params.id as string
  try {
    cadastro.value = await consultarCadastroGabinete(id)
    if (cadastro.value.status === 'concluido' && cadastro.value.api_base_url) {
      setTenantApiBaseUrl(cadastro.value.api_base_url)
    }
    if (cadastro.value.status === 'concluido' || cadastro.value.status === 'falhou') {
      if (timer) {
        clearInterval(timer)
        timer = null
      }
    }
  } catch {
    erro.value = 'Cadastro não encontrado.'
    if (timer) clearInterval(timer)
  }
}

function irParaLogin() {
  if (cadastro.value?.app_url_sugerida) {
    window.location.href = cadastro.value.app_url_sugerida
    return
  }
  if (cadastro.value?.domain) {
    const port = (import.meta.env.VITE_DEV_PORT as string | undefined) || '5174'
    window.location.href = `http://${cadastro.value.domain}:${port}/login`
  }
}

onMounted(() => {
  carregar()
  timer = setInterval(carregar, 2500)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-slate-900 flex items-center justify-center p-6">
    <div class="max-w-lg w-full card p-8 text-center">
      <template v-if="erro">
        <XCircle class="w-12 h-12 text-red-500 mx-auto mb-4" />
        <p class="text-gray-700 dark:text-slate-300">{{ erro }}</p>
        <RouterLink to="/cadastro-gabinete" class="btn btn-primary mt-6 inline-block">
          Voltar ao cadastro
        </RouterLink>
      </template>

      <template v-else-if="!cadastro">
        <Loader2 class="w-10 h-10 animate-spin text-primary-600 mx-auto" />
        <p class="mt-4 text-gray-600 dark:text-slate-400">Carregando…</p>
      </template>

      <template v-else-if="cadastro.status === 'falhou'">
        <XCircle class="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h1 class="text-xl font-bold text-gray-900 dark:text-slate-100">Falha no provisionamento</h1>
        <p class="text-sm text-gray-600 dark:text-slate-400 mt-2">{{ cadastro.erro_mensagem || 'Erro desconhecido.' }}</p>
        <RouterLink to="/cadastro-gabinete" class="btn btn-primary mt-6 inline-block">
          Tentar novamente
        </RouterLink>
      </template>

      <template v-else-if="cadastro.status === 'concluido'">
        <CheckCircle class="w-12 h-12 text-green-500 mx-auto mb-4" />
        <h1 class="text-xl font-bold text-gray-900 dark:text-slate-100">Gabinete pronto!</h1>
        <img
          v-if="cadastro.logo"
          :src="cadastro.logo"
          alt="Logo do gabinete"
          class="w-20 h-20 object-contain mx-auto mt-4 rounded-lg border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-1"
        >
        <p class="text-sm text-gray-600 dark:text-slate-400 mt-2">
          <strong>{{ cadastro.nome_gabinete }}</strong> em
          <code class="text-xs bg-gray-100 dark:bg-slate-800 px-1 rounded">{{ cadastro.domain }}</code>
        </p>
        <p class="text-xs text-gray-500 dark:text-slate-500 mt-4">
          Use o e-mail <strong>{{ cadastro.admin_email }}</strong> e a senha definida no cadastro.
        </p>
        <button type="button" class="btn btn-primary mt-6 w-full flex items-center justify-center gap-2" @click="irParaLogin">
          <ExternalLink class="w-4 h-4" />
          Ir para o login do gabinete
        </button>
        <p class="text-xs text-gray-500 mt-4">
          Se o link não abrir, acesse pelo endereço do seu gabinete na porta do front (ex.: :5174).
        </p>
      </template>

      <template v-else>
        <Loader2 class="w-10 h-10 animate-spin text-primary-600 mx-auto" />
        <h1 class="text-xl font-bold text-gray-900 dark:text-slate-100 mt-4">Preparando seu ambiente…</h1>
        <p class="text-sm text-gray-600 dark:text-slate-400 mt-2">
          Status: {{ cadastro.status }} — banco, permissões e administrador.
        </p>
      </template>
    </div>
  </div>
</template>
