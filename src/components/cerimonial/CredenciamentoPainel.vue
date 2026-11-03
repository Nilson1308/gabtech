<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useCerimonialStore } from '@/stores/cerimonial'
import type { CredenciamentoConfig } from '@/constants/credenciamento'
import { normalizeCredenciamentoConfig, urlPoliticaPrivacidade } from '@/constants/credenciamento'
import { useAlertDialog } from '@/composables/useAlertDialog'
import QRCode from 'qrcode'
import { QrCode, Users, UserCheck, Download, Search, CheckCircle2, FileDown, Settings2, Save } from 'lucide-vue-next'

interface Props {
  eventoId: string
}

const props = defineProps<Props>()

const cerimonialStore = useCerimonialStore()
const { showSuccess, showError } = useAlertDialog()

const qrCodeDataUrl = ref('')
const buscaCredenciado = ref('')
const salvandoConfig = ref(false)
const configLocal = ref<CredenciamentoConfig>(normalizeCredenciamentoConfig())

const evento = computed(() => cerimonialStore.getEventoById(props.eventoId))

const totalRegistrados = computed(() => 
  cerimonialStore.totalCredenciados(props.eventoId)
)

const totalPresentes = computed(() => 
  cerimonialStore.totalPresentes(props.eventoId)
)

const credenciados = computed(() => {
  if (!evento.value) return []
  
  let lista = [...evento.value.credenciados]
  
  // Filtrar por busca
  if (buscaCredenciado.value.trim()) {
    const termo = buscaCredenciado.value.toLowerCase()
    const digits = termo.replace(/\D/g, '')
    lista = lista.filter(c =>
      c.nome.toLowerCase().includes(termo) ||
      c.telefone.includes(digits) ||
      (c.email && c.email.toLowerCase().includes(termo)) ||
      (c.orgao_instituicao && c.orgao_instituicao.toLowerCase().includes(termo)) ||
      (c.cpf && c.cpf.includes(digits)),
    )
  }
  
  // Ordenar por data de registro (mais recentes primeiro)
  return lista.sort((a, b) => {
    return new Date(b.data_registro).getTime() - new Date(a.data_registro).getTime()
  })
})

watch(
  () => evento.value?.credenciamentoConfig,
  cfg => {
    if (cfg) configLocal.value = { ...cfg }
  },
  { immediate: true },
)

const previewPoliticaUrl = computed(() =>
  urlPoliticaPrivacidade(configLocal.value, props.eventoId),
)

onMounted(async () => {
  await gerarQRCode()
})

async function salvarConfigCredenciamento() {
  salvandoConfig.value = true
  try {
    await cerimonialStore.atualizarCredenciamentoConfig(props.eventoId, {
      ...configLocal.value,
      url_politica_privacidade: configLocal.value.url_politica_privacidade.trim(),
    })
    showSuccess('Parâmetros do formulário público salvos.')
  } catch (e: unknown) {
    showError(e instanceof Error ? e.message : 'Não foi possível salvar os parâmetros.')
  } finally {
    salvandoConfig.value = false
  }
}

async function gerarQRCode() {
  try {
    // URL pública de credenciamento
    const urlCredenciamento = `${window.location.origin}/evento/${props.eventoId}/credenciamento`
    
    // Gerar QR Code em alta resolução
    qrCodeDataUrl.value = await QRCode.toDataURL(urlCredenciamento, {
      width: 800,
      margin: 2,
      color: {
        dark: '#000000',
        light: '#FFFFFF'
      },
      errorCorrectionLevel: 'H'
    })
  } catch (error) {
    console.error('Erro ao gerar QR Code:', error)
  }
}

async function baixarQRCode() {
  if (!qrCodeDataUrl.value) return
  
  const link = document.createElement('a')
  link.href = qrCodeDataUrl.value
  link.download = `qrcode-evento-${props.eventoId}.png`
  link.click()
}

function formatarCPF(cpf?: string) {
  if (!cpf || cpf.length < 11) return '—'
  return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4')
}

function formatarTelefone(tel: string) {
  if (tel.length === 11) {
    return tel.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3')
  }
  return tel.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3')
}

function formatarDataHora(data: string) {
  return new Date(data).toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function exportarCSV() {
  if (!evento.value) return
  
  const headers = [
    'Nome',
    'Telefone',
    'E-mail',
    'Nascimento',
    'Órgão/Instituição',
    'Data/Hora Registo',
    'Status',
    'LGPD',
  ]
  const rows = evento.value.credenciados.map(c => [
    c.nome,
    formatarTelefone(c.telefone),
    c.email || '',
    c.data_nascimento || '',
    c.orgao_instituicao || '',
    formatarDataHora(c.data_registro),
    c.status_presenca === 'presente' ? 'Presente' : 'Pendente',
    c.aceitou_lgpd ? 'Sim' : 'Não',
  ])
  
  let csv = headers.join(',') + '\n'
  rows.forEach(row => {
    csv += row.map(cell => `"${cell}"`).join(',') + '\n'
  })
  
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `credenciados-evento-${props.eventoId}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

function copiarLink() {
  const urlCredenciamento = `${window.location.origin}/evento/${props.eventoId}/credenciamento`
  navigator.clipboard.writeText(urlCredenciamento)
  // Poderia adicionar um toast de sucesso aqui
}
</script>

<template>
  <div class="space-y-6">
    <!-- KPIs Rápidos -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-900/30 rounded-xl p-6 border border-blue-200 dark:border-blue-800">
        <div class="flex items-center gap-4">
          <div class="p-3 bg-blue-500 dark:bg-blue-600 rounded-lg">
            <Users class="w-8 h-8 text-white" />
          </div>
          <div>
            <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ totalRegistrados }}</p>
            <p class="text-sm text-blue-700 dark:text-blue-300">Total Registados</p>
          </div>
        </div>
      </div>

      <div class="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-900/30 rounded-xl p-6 border border-green-200 dark:border-green-800">
        <div class="flex items-center gap-4">
          <div class="p-3 bg-green-500 dark:bg-green-600 rounded-lg">
            <UserCheck class="w-8 h-8 text-white" />
          </div>
          <div>
            <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ totalPresentes }}</p>
            <p class="text-sm text-green-700 dark:text-green-300">Presentes (Check-in)</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Parâmetros do formulário público -->
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
        <Settings2 class="w-5 h-5 text-primary-600 dark:text-primary-400" />
        Formulário público de credenciamento
      </h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
        Nome e telefone/WhatsApp são sempre solicitados. Escolha quais campos adicionais exibir no link e no QR Code.
      </p>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
        <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer">
          <input v-model="configLocal.mostrar_email" type="checkbox" class="rounded text-primary-600" />
          E-mail
        </label>
        <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer">
          <input v-model="configLocal.mostrar_data_nascimento" type="checkbox" class="rounded text-primary-600" />
          Data de nascimento
        </label>
        <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer">
          <input v-model="configLocal.mostrar_orgao_instituicao" type="checkbox" class="rounded text-primary-600" />
          Órgão / instituição
        </label>
      </div>

      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          URL da política de privacidade (opcional)
        </label>
        <input
          v-model="configLocal.url_politica_privacidade"
          type="url"
          placeholder="https://... (deixe vazio para usar a política padrão GabTech)"
          class="w-full px-3 py-2 text-sm bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg"
        />
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
          Padrão:
          <a :href="previewPoliticaUrl" target="_blank" rel="noopener" class="text-primary-600 dark:text-primary-400 underline">
            {{ previewPoliticaUrl }}
          </a>
        </p>
      </div>

      <button
        type="button"
        :disabled="salvandoConfig"
        class="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg disabled:opacity-50"
        @click="salvarConfigCredenciamento"
      >
        <Save class="w-4 h-4" />
        {{ salvandoConfig ? 'Salvando…' : 'Salvar parâmetros' }}
      </button>
    </div>

    <!-- Layout Principal -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Lado Esquerdo: QR Code -->
      <div class="space-y-4">
        <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <QrCode class="w-5 h-5 text-primary-600 dark:text-primary-400" />
            QR Code de Credenciamento
          </h3>

          <!-- QR Code -->
          <div class="flex justify-center mb-6">
            <div v-if="qrCodeDataUrl" class="bg-white p-6 rounded-lg shadow-lg">
              <img :src="qrCodeDataUrl" alt="QR Code" class="w-64 h-64" />
            </div>
            <div v-else class="w-64 h-64 bg-gray-100 dark:bg-gray-700 rounded-lg animate-pulse"></div>
          </div>

          <!-- Ações QR Code -->
          <div class="space-y-3">
            <button
              @click="baixarQRCode"
              :disabled="!qrCodeDataUrl"
              class="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
            >
              <Download class="w-5 h-5" />
              Descarregar QR Code (Alta Resolução)
            </button>

            <button
              @click="copiarLink"
              class="w-full flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 font-medium rounded-lg transition-all"
            >
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Copiar Link de Credenciamento
            </button>
          </div>

          <!-- Info -->
          <div class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <p class="text-xs text-blue-700 dark:text-blue-300">
              <strong>Auto Check-in:</strong> Ao escanear o QR Code e preencher o formulário, o cidadão já fica automaticamente registado como "Presente". O painel à direita mostra os registos em tempo real.
            </p>
          </div>
        </div>
      </div>

      <!-- Lado Direito: Lista e Check-in -->
      <div class="space-y-4">
        <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <UserCheck class="w-5 h-5 text-primary-600 dark:text-primary-400" />
              Monitor de Check-ins (Tempo Real)
            </h3>
            <button
              @click="exportarCSV"
              class="flex items-center gap-2 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-all"
            >
              <FileDown class="w-4 h-4" />
              Exportar CSV
            </button>
          </div>

          <!-- Barra de Pesquisa -->
          <div class="relative mb-4">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              v-model="buscaCredenciado"
              type="text"
              placeholder="Pesquisar por nome, telefone ou e-mail..."
              class="w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all text-gray-900 dark:text-white"
            />
          </div>

          <!-- Lista de Credenciados -->
          <div class="space-y-2 max-h-[600px] overflow-y-auto">
            <div
              v-for="cred in credenciados"
              :key="cred.id"
              :class="[
                'p-4 rounded-lg border transition-all',
                cred.status_presenca === 'presente'
                  ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                  : 'bg-gray-50 dark:bg-gray-900/50 border-gray-200 dark:border-gray-700'
              ]"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1">
                    <h4 class="font-semibold text-gray-900 dark:text-white truncate">
                      {{ cred.nome }}
                    </h4>
                    <CheckCircle2
                      v-if="cred.status_presenca === 'presente'"
                      class="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0"
                    />
                  </div>
                  <div class="space-y-1">
                    <p class="text-sm text-gray-600 dark:text-gray-400">
                      <span class="font-medium">Tel:</span> {{ formatarTelefone(cred.telefone) }}
                    </p>
                    <p v-if="cred.email" class="text-sm text-gray-600 dark:text-gray-400">
                      <span class="font-medium">E-mail:</span> {{ cred.email }}
                    </p>
                    <p v-if="cred.orgao_instituicao" class="text-sm text-gray-600 dark:text-gray-400">
                      <span class="font-medium">Órgão:</span> {{ cred.orgao_instituicao }}
                    </p>
                    <p v-if="cred.data_nascimento" class="text-sm text-gray-600 dark:text-gray-400">
                      <span class="font-medium">Nasc.:</span>
                      {{ new Date(cred.data_nascimento + 'T12:00:00').toLocaleDateString('pt-BR') }}
                    </p>
                    <p v-if="cred.cpf" class="text-xs text-gray-500 dark:text-gray-500">
                      CPF (legado): {{ formatarCPF(cred.cpf) }}
                    </p>
                    <p class="text-xs text-gray-500 dark:text-gray-500">
                      Check-in em {{ formatarDataHora(cred.data_registro) }}
                    </p>
                  </div>
                </div>

                <!-- Badge Status (Read-only) -->
                <div class="flex-shrink-0 px-4 py-2 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-sm font-medium rounded-lg flex items-center gap-2">
                  <CheckCircle2 class="w-4 h-4" />
                  Presente
                </div>
              </div>
            </div>

            <!-- Estado vazio -->
            <div v-if="credenciados.length === 0" class="text-center py-12">
              <Users class="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-3" />
              <p class="text-gray-500 dark:text-gray-400">
                {{ buscaCredenciado ? 'Nenhum resultado encontrado' : 'Nenhum credenciamento registado ainda' }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
