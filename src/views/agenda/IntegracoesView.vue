<script setup lang="ts">
import { ref } from 'vue'
import Button from '@/components/common/Button.vue'
import { Cloud, CheckCircle, AlertCircle, Info } from 'lucide-vue-next'

// Estado das integrações (mockado)
const integracoes = ref({
  google: {
    conectado: false,
    email: '',
    ultimaSync: null as string | null
  },
  outlook: {
    conectado: false,
    email: '',
    ultimaSync: null as string | null
  }
})

const loading = ref(false)
const mensagem = ref({ tipo: '', texto: '' })

// Methods
const conectarGoogle = async () => {
  loading.value = true
  mensagem.value = { tipo: '', texto: '' }
  
  // Simulação de OAuth flow
  await new Promise(resolve => setTimeout(resolve, 1500))
  
  integracoes.value.google = {
    conectado: true,
    email: 'gabinete@gabinete.gov.br',
    ultimaSync: new Date().toISOString()
  }
  
  loading.value = false
  mensagem.value = {
    tipo: 'success',
    texto: 'Google Calendar conectado com sucesso!'
  }
  
  setTimeout(() => {
    mensagem.value = { tipo: '', texto: '' }
  }, 5000)
}

const desconectarGoogle = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  
  integracoes.value.google = {
    conectado: false,
    email: '',
    ultimaSync: null
  }
  
  loading.value = false
  mensagem.value = {
    tipo: 'info',
    texto: 'Google Calendar desconectado'
  }
  
  setTimeout(() => {
    mensagem.value = { tipo: '', texto: '' }
  }, 3000)
}

const conectarOutlook = async () => {
  loading.value = true
  mensagem.value = { tipo: '', texto: '' }
  
  // Simulação de OAuth flow
  await new Promise(resolve => setTimeout(resolve, 1500))
  
  integracoes.value.outlook = {
    conectado: true,
    email: 'gabinete@gabinete.gov.br',
    ultimaSync: new Date().toISOString()
  }
  
  loading.value = false
  mensagem.value = {
    tipo: 'success',
    texto: 'Outlook Calendar conectado com sucesso!'
  }
  
  setTimeout(() => {
    mensagem.value = { tipo: '', texto: '' }
  }, 5000)
}

const desconectarOutlook = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  
  integracoes.value.outlook = {
    conectado: false,
    email: '',
    ultimaSync: null
  }
  
  loading.value = false
  mensagem.value = {
    tipo: 'info',
    texto: 'Outlook Calendar desconectado'
  }
  
  setTimeout(() => {
    mensagem.value = { tipo: '', texto: '' }
  }, 3000)
}

const sincronizarAgora = async (servico: 'google' | 'outlook') => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  if (servico === 'google') {
    integracoes.value.google.ultimaSync = new Date().toISOString()
  } else {
    integracoes.value.outlook.ultimaSync = new Date().toISOString()
  }
  
  loading.value = false
  mensagem.value = {
    tipo: 'success',
    texto: `Sincronização com ${servico === 'google' ? 'Google' : 'Outlook'} concluída!`
  }
  
  setTimeout(() => {
    mensagem.value = { tipo: '', texto: '' }
  }, 3000)
}

const formatarDataSync = (dataISO: string | null) => {
  if (!dataISO) return 'Nunca'
  
  const data = new Date(dataISO)
  return data.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <p class="text-sm text-gray-600 dark:text-slate-400">
        Sincronize eventos com Google Calendar e Microsoft Outlook
      </p>
    </div>

    <!-- Mensagem de Feedback -->
    <div
      v-if="mensagem.texto"
      :class="[
        mensagem.tipo === 'success'
          ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
          : mensagem.tipo === 'info'
          ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
          : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800',
        'p-4 border rounded-lg flex items-start gap-3 animate-fade-in'
      ]"
    >
      <CheckCircle
        v-if="mensagem.tipo === 'success'"
        class="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5"
      />
      <Info
        v-else-if="mensagem.tipo === 'info'"
        class="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5"
      />
      <AlertCircle
        v-else
        class="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5"
      />
      <p
        :class="[
          mensagem.tipo === 'success'
            ? 'text-green-900 dark:text-green-300'
            : mensagem.tipo === 'info'
            ? 'text-blue-900 dark:text-blue-300'
            : 'text-red-900 dark:text-red-300',
          'text-sm font-medium'
        ]"
      >
        {{ mensagem.texto }}
      </p>
    </div>

    <!-- Informações -->
    <div class="card p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
      <div class="flex items-start gap-3">
        <Info class="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
        <div class="text-sm text-blue-900 dark:text-blue-300">
          <p class="font-medium mb-1">Como funciona a sincronização:</p>
          <ul class="list-disc list-inside space-y-1 text-blue-800 dark:text-blue-400">
            <li>Eventos criados no GabTech podem ser exportados automaticamente</li>
            <li>A sincronização bidirecional mantém tudo atualizado</li>
            <li>Alterações feitas externamente são importadas periodicamente</li>
            <li>Ícones indicam quais eventos estão sincronizados</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Grid de Integrações -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Google Calendar -->
      <div class="card">
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center gap-3">
            <div class="w-16 h-16 bg-white dark:bg-slate-700 rounded-xl flex items-center justify-center border-2 border-gray-200 dark:border-slate-600">
              <svg class="w-10 h-10" viewBox="0 0 24 24" fill="none">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z" fill="#4285F4"/>
                <path d="M12.5 7H11v6l5.25 3.15.75-1.23-4.5-2.67z" fill="#4285F4"/>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900 dark:text-slate-100">
                Google Calendar
              </h3>
              <p class="text-sm text-gray-600 dark:text-slate-400">
                Sincronização bidirecional
              </p>
            </div>
          </div>
          
          <span
            v-if="integracoes.google.conectado"
            class="inline-flex items-center gap-1 px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-full text-xs font-medium"
          >
            <CheckCircle class="w-3 h-3" />
            Conectado
          </span>
        </div>

        <div v-if="integracoes.google.conectado" class="space-y-4">
          <div class="p-3 bg-gray-50 dark:bg-slate-900 rounded-lg">
            <p class="text-sm text-gray-600 dark:text-slate-400 mb-1">Conta conectada:</p>
            <p class="text-sm font-medium text-gray-900 dark:text-slate-100">
              {{ integracoes.google.email }}
            </p>
            <p class="text-xs text-gray-500 dark:text-slate-500 mt-2">
              Última sincronização: {{ formatarDataSync(integracoes.google.ultimaSync) }}
            </p>
          </div>

          <div class="flex gap-2">
            <Button
              variant="secondary"
              class="flex-1"
              @click="sincronizarAgora('google')"
              :disabled="loading"
            >
              Sincronizar Agora
            </Button>
            <Button
              variant="secondary"
              @click="desconectarGoogle"
              :disabled="loading"
            >
              Desconectar
            </Button>
          </div>
        </div>

        <div v-else>
          <p class="text-sm text-gray-600 dark:text-slate-400 mb-4">
            Conecte sua conta do Google para sincronizar eventos automaticamente
          </p>
          <Button
            variant="primary"
            class="w-full"
            @click="conectarGoogle"
            :disabled="loading"
          >
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z"/>
            </svg>
            Conectar com Google
          </Button>
        </div>
      </div>

      <!-- Microsoft Outlook -->
      <div class="card">
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center gap-3">
            <div class="w-16 h-16 bg-white dark:bg-slate-700 rounded-xl flex items-center justify-center border-2 border-gray-200 dark:border-slate-600">
              <svg class="w-10 h-10" viewBox="0 0 24 24" fill="none">
                <path d="M7 4C5.34 4 4 5.34 4 7v10c0 1.66 1.34 3 3 3h10c1.66 0 3-1.34 3-3V7c0-1.66-1.34-3-3-3H7z" fill="#0078D4"/>
                <path d="M12 8c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4-1.79-4-4-4zm0 6c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z" fill="white"/>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900 dark:text-slate-100">
                Outlook Calendar
              </h3>
              <p class="text-sm text-gray-600 dark:text-slate-400">
                Microsoft 365 / Outlook.com
              </p>
            </div>
          </div>
          
          <span
            v-if="integracoes.outlook.conectado"
            class="inline-flex items-center gap-1 px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-full text-xs font-medium"
          >
            <CheckCircle class="w-3 h-3" />
            Conectado
          </span>
        </div>

        <div v-if="integracoes.outlook.conectado" class="space-y-4">
          <div class="p-3 bg-gray-50 dark:bg-slate-900 rounded-lg">
            <p class="text-sm text-gray-600 dark:text-slate-400 mb-1">Conta conectada:</p>
            <p class="text-sm font-medium text-gray-900 dark:text-slate-100">
              {{ integracoes.outlook.email }}
            </p>
            <p class="text-xs text-gray-500 dark:text-slate-500 mt-2">
              Última sincronização: {{ formatarDataSync(integracoes.outlook.ultimaSync) }}
            </p>
          </div>

          <div class="flex gap-2">
            <Button
              variant="secondary"
              class="flex-1"
              @click="sincronizarAgora('outlook')"
              :disabled="loading"
            >
              Sincronizar Agora
            </Button>
            <Button
              variant="secondary"
              @click="desconectarOutlook"
              :disabled="loading"
            >
              Desconectar
            </Button>
          </div>
        </div>

        <div v-else>
          <p class="text-sm text-gray-600 dark:text-slate-400 mb-4">
            Conecte sua conta Microsoft para sincronizar eventos automaticamente
          </p>
          <Button
            variant="primary"
            class="w-full"
            @click="conectarOutlook"
            :disabled="loading"
          >
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M24 7.387v9.226a.389.389 0 01-.387.387h-.062V8.065h-9.742V16h-.775a.389.389 0 01-.389-.387V7.387c0-.214.174-.387.389-.387h10.58c.214 0 .387.173.387.387z"/>
            </svg>
            Conectar com Microsoft
          </Button>
        </div>
      </div>
    </div>

    <!-- Recursos Premium -->
    <div class="card bg-gradient-to-r from-primary-50 to-purple-50 dark:from-primary-900/20 dark:to-purple-900/20 border-primary-200 dark:border-primary-800">
      <div class="flex items-start gap-4">
        <div class="w-12 h-12 bg-gradient-to-br from-primary-600 to-purple-600 rounded-xl flex items-center justify-center flex-shrink-0">
          <Cloud class="w-6 h-6 text-white" />
        </div>
        <div class="flex-1">
          <h4 class="text-lg font-bold text-gray-900 dark:text-slate-100 mb-2">
            Sincronização Automática Premium
          </h4>
          <p class="text-sm text-gray-700 dark:text-slate-300 mb-3">
            Na versão de produção, a sincronização ocorre automaticamente a cada 5 minutos, mantendo todos os calendários sempre atualizados.
          </p>
          <ul class="space-y-2 text-sm text-gray-600 dark:text-slate-400">
            <li class="flex items-center gap-2">
              <CheckCircle class="w-4 h-4 text-green-600 dark:text-green-400" />
              Sincronização bidirecional em tempo real
            </li>
            <li class="flex items-center gap-2">
              <CheckCircle class="w-4 h-4 text-green-600 dark:text-green-400" />
              Suporte a múltiplos calendários
            </li>
            <li class="flex items-center gap-2">
              <CheckCircle class="w-4 h-4 text-green-600 dark:text-green-400" />
              Detecção e resolução automática de conflitos
            </li>
            <li class="flex items-center gap-2">
              <CheckCircle class="w-4 h-4 text-green-600 dark:text-green-400" />
              Notificações e lembretes sincronizados
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}
</style>
