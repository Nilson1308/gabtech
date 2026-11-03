<script setup lang="ts">
import { ref } from 'vue'
import Button from '@/components/common/Button.vue'
import { Mail, MessageSquare, MessageCircle, CheckCircle, AlertCircle, Info } from 'lucide-vue-next'

// Estado das integrações (mockado)
const integracoes = ref({
  email: {
    conectado: false,
    provedor: '',
    email: '',
    ultimaSync: null as string | null
  },
  whatsapp: {
    conectado: false,
    numero: '',
    ultimaSync: null as string | null
  },
  sms: {
    conectado: false,
    provedor: '',
    ultimaSync: null as string | null
  }
})

const loading = ref(false)
const mensagem = ref({ tipo: '', texto: '' })

// Methods Email
const conectarEmail = async () => {
  loading.value = true
  mensagem.value = { tipo: '', texto: '' }
  
  await new Promise(resolve => setTimeout(resolve, 1500))
  
  integracoes.value.email = {
    conectado: true,
    provedor: 'Gmail / SMTP',
    email: 'gabinete@gabinete.gov.br',
    ultimaSync: new Date().toISOString()
  }
  
  loading.value = false
  mensagem.value = {
    tipo: 'success',
    texto: 'Email conectado com sucesso!'
  }
  
  setTimeout(() => {
    mensagem.value = { tipo: '', texto: '' }
  }, 5000)
}

const desconectarEmail = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  
  integracoes.value.email = {
    conectado: false,
    provedor: '',
    email: '',
    ultimaSync: null
  }
  
  loading.value = false
  mensagem.value = {
    tipo: 'info',
    texto: 'Email desconectado'
  }
  
  setTimeout(() => {
    mensagem.value = { tipo: '', texto: '' }
  }, 3000)
}

// Methods WhatsApp
const conectarWhatsApp = async () => {
  loading.value = true
  mensagem.value = { tipo: '', texto: '' }
  
  await new Promise(resolve => setTimeout(resolve, 1500))
  
  integracoes.value.whatsapp = {
    conectado: true,
    numero: '+55 (61) 99999-9999',
    ultimaSync: new Date().toISOString()
  }
  
  loading.value = false
  mensagem.value = {
    tipo: 'success',
    texto: 'WhatsApp Business conectado com sucesso!'
  }
  
  setTimeout(() => {
    mensagem.value = { tipo: '', texto: '' }
  }, 5000)
}

const desconectarWhatsApp = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  
  integracoes.value.whatsapp = {
    conectado: false,
    numero: '',
    ultimaSync: null
  }
  
  loading.value = false
  mensagem.value = {
    tipo: 'info',
    texto: 'WhatsApp desconectado'
  }
  
  setTimeout(() => {
    mensagem.value = { tipo: '', texto: '' }
  }, 3000)
}

// Methods SMS
const conectarSMS = async () => {
  loading.value = true
  mensagem.value = { tipo: '', texto: '' }
  
  await new Promise(resolve => setTimeout(resolve, 1500))
  
  integracoes.value.sms = {
    conectado: true,
    provedor: 'Twilio',
    ultimaSync: new Date().toISOString()
  }
  
  loading.value = false
  mensagem.value = {
    tipo: 'success',
    texto: 'Provedor SMS conectado com sucesso!'
  }
  
  setTimeout(() => {
    mensagem.value = { tipo: '', texto: '' }
  }, 5000)
}

const desconectarSMS = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  
  integracoes.value.sms = {
    conectado: false,
    provedor: '',
    ultimaSync: null
  }
  
  loading.value = false
  mensagem.value = {
    tipo: 'info',
    texto: 'Provedor SMS desconectado'
  }
  
  setTimeout(() => {
    mensagem.value = { tipo: '', texto: '' }
  }, 3000)
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <p class="text-sm text-gray-600 dark:text-slate-400">
        Configure canais de comunicação para envio de notificações, convites e lembretes
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
          <p class="font-medium mb-1">Canais de Comunicação Disponíveis:</p>
          <ul class="list-disc list-inside space-y-1 text-blue-800 dark:text-blue-400">
            <li>Email: Envio de convites formais e notificações</li>
            <li>WhatsApp Business: Comunicação direta e lembretes</li>
            <li>SMS: Notificações urgentes e confirmações</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Grid de Integrações -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Email -->
      <div class="card">
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center gap-3">
            <div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
              <Mail class="w-8 h-8 text-white" />
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900 dark:text-slate-100">
                Email
              </h3>
              <p class="text-sm text-gray-600 dark:text-slate-400">
                SMTP / Gmail
              </p>
            </div>
          </div>
          
          <span
            v-if="integracoes.email.conectado"
            class="inline-flex items-center gap-1 px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-full text-xs font-medium"
          >
            <CheckCircle class="w-3 h-3" />
            Conectado
          </span>
        </div>

        <div v-if="integracoes.email.conectado" class="space-y-4">
          <div class="p-3 bg-gray-50 dark:bg-slate-900 rounded-lg">
            <p class="text-sm text-gray-600 dark:text-slate-400 mb-1">Email configurado:</p>
            <p class="text-sm font-medium text-gray-900 dark:text-slate-100">
              {{ integracoes.email.email }}
            </p>
            <p class="text-xs text-gray-500 dark:text-slate-500 mt-2">
              Provedor: {{ integracoes.email.provedor }}
            </p>
          </div>

          <div class="flex gap-2">
            <Button
              variant="secondary"
              class="flex-1"
              @click="desconectarEmail"
              :disabled="loading"
            >
              Desconectar
            </Button>
          </div>
        </div>

        <div v-else>
          <p class="text-sm text-gray-600 dark:text-slate-400 mb-4">
            Configure o servidor SMTP ou conecte com Gmail para envio de emails
          </p>
          <Button
            variant="primary"
            class="w-full"
            @click="conectarEmail"
            :disabled="loading"
          >
            <Mail class="w-5 h-5" />
            Configurar Email
          </Button>
        </div>
      </div>

      <!-- WhatsApp Business -->
      <div class="card">
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center gap-3">
            <div class="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center shadow-lg">
              <MessageSquare class="w-8 h-8 text-white" />
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900 dark:text-slate-100">
                WhatsApp
              </h3>
              <p class="text-sm text-gray-600 dark:text-slate-400">
                Business API
              </p>
            </div>
          </div>
          
          <span
            v-if="integracoes.whatsapp.conectado"
            class="inline-flex items-center gap-1 px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-full text-xs font-medium"
          >
            <CheckCircle class="w-3 h-3" />
            Conectado
          </span>
        </div>

        <div v-if="integracoes.whatsapp.conectado" class="space-y-4">
          <div class="p-3 bg-gray-50 dark:bg-slate-900 rounded-lg">
            <p class="text-sm text-gray-600 dark:text-slate-400 mb-1">Número conectado:</p>
            <p class="text-sm font-medium text-gray-900 dark:text-slate-100">
              {{ integracoes.whatsapp.numero }}
            </p>
            <p class="text-xs text-gray-500 dark:text-slate-500 mt-2">
              WhatsApp Business API
            </p>
          </div>

          <div class="flex gap-2">
            <Button
              variant="secondary"
              class="flex-1"
              @click="desconectarWhatsApp"
              :disabled="loading"
            >
              Desconectar
            </Button>
          </div>
        </div>

        <div v-else>
          <p class="text-sm text-gray-600 dark:text-slate-400 mb-4">
            Conecte sua conta WhatsApp Business para envio de mensagens
          </p>
          <Button
            variant="primary"
            class="w-full"
            @click="conectarWhatsApp"
            :disabled="loading"
          >
            <MessageSquare class="w-5 h-5" />
            Conectar WhatsApp
          </Button>
        </div>
      </div>

      <!-- SMS -->
      <div class="card">
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center gap-3">
            <div class="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
              <MessageCircle class="w-8 h-8 text-white" />
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900 dark:text-slate-100">
                SMS
              </h3>
              <p class="text-sm text-gray-600 dark:text-slate-400">
                Twilio / Zenvia
              </p>
            </div>
          </div>
          
          <span
            v-if="integracoes.sms.conectado"
            class="inline-flex items-center gap-1 px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-full text-xs font-medium"
          >
            <CheckCircle class="w-3 h-3" />
            Conectado
          </span>
        </div>

        <div v-if="integracoes.sms.conectado" class="space-y-4">
          <div class="p-3 bg-gray-50 dark:bg-slate-900 rounded-lg">
            <p class="text-sm text-gray-600 dark:text-slate-400 mb-1">Provedor:</p>
            <p class="text-sm font-medium text-gray-900 dark:text-slate-100">
              {{ integracoes.sms.provedor }}
            </p>
            <p class="text-xs text-gray-500 dark:text-slate-500 mt-2">
              API configurada e ativa
            </p>
          </div>

          <div class="flex gap-2">
            <Button
              variant="secondary"
              class="flex-1"
              @click="desconectarSMS"
              :disabled="loading"
            >
              Desconectar
            </Button>
          </div>
        </div>

        <div v-else>
          <p class="text-sm text-gray-600 dark:text-slate-400 mb-4">
            Configure provedor de SMS para notificações urgentes
          </p>
          <Button
            variant="primary"
            class="w-full"
            @click="conectarSMS"
            :disabled="loading"
          >
            <MessageCircle class="w-5 h-5" />
            Configurar SMS
          </Button>
        </div>
      </div>
    </div>

    <!-- Recursos de Comunicação -->
    <div class="card bg-gradient-to-r from-primary-50 to-purple-50 dark:from-primary-900/20 dark:to-purple-900/20 border-primary-200 dark:border-primary-800">
      <div class="flex items-start gap-4">
        <div class="w-12 h-12 bg-gradient-to-br from-primary-600 to-purple-600 rounded-xl flex items-center justify-center flex-shrink-0">
          <MessageSquare class="w-6 h-6 text-white" />
        </div>
        <div class="flex-1">
          <h4 class="text-lg font-bold text-gray-900 dark:text-slate-100 mb-2">
            Disparo Automático de Comunicações
          </h4>
          <p class="text-sm text-gray-700 dark:text-slate-300 mb-3">
            Na versão de produção, você poderá configurar templates e disparos automáticos de convites, lembretes e notificações através de todos os canais.
          </p>
          <ul class="space-y-2 text-sm text-gray-600 dark:text-slate-400">
            <li class="flex items-center gap-2">
              <CheckCircle class="w-4 h-4 text-green-600 dark:text-green-400" />
              Templates personalizáveis por tipo de comunicação
            </li>
            <li class="flex items-center gap-2">
              <CheckCircle class="w-4 h-4 text-green-600 dark:text-green-400" />
              Agendamento de disparos em massa
            </li>
            <li class="flex items-center gap-2">
              <CheckCircle class="w-4 h-4 text-green-600 dark:text-green-400" />
              Variáveis dinâmicas (nome, data, local, etc)
            </li>
            <li class="flex items-center gap-2">
              <CheckCircle class="w-4 h-4 text-green-600 dark:text-green-400" />
              Tracking de entrega e confirmação de leitura
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
