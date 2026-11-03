<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAtendimentosStore } from '@/stores/atendimentos'
import { useAuthStore } from '@/stores/auth'
import { PERMS } from '@/constants/rbac'
import type { Atendimento, StatusAtendimento } from '@/types'
import RastreabilidadeMeta from '@/components/common/RastreabilidadeMeta.vue'
import { AUDITORIA_ALVO } from '@/services/auditoria'
import { useFormatters } from '@/composables/useFormatters'
import { useAlertDialog } from '@/composables/useAlertDialog'
import Avatar from '@/components/common/Avatar.vue'
import Badge from '@/components/common/Badge.vue'
import DespachosTimeline from '@/components/atendimentos/DespachosTimeline.vue'
import AtendimentoModal from '@/components/atendimentos/AtendimentoModal.vue'
import {
  MENSAGEM_SAIR_STATUS_ABERTO,
  TITULO_SAIR_STATUS_ABERTO,
} from '@/constants/atendimentos'
import { 
  ArrowLeft, 
  AlertCircle,
  CheckCircle,
  Trash2,
  Paperclip,
  Pencil,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const atendimentosStore = useAtendimentosStore()
const authStore = useAuthStore()
const { formatDate } = useFormatters()
const { showConfirm, showSuccess, showError } = useAlertDialog()

// Estado
const atendimento = ref<Atendimento | null>(null)
const loading = ref(true)
const alterandoStatus = ref(false)
const mostrarModalEditar = ref(false)
const statusSelectKey = ref(0)

// Perfil ativo do cidadão neste atendimento
const perfilAtivo = computed(() => {
  if (!atendimento.value?.perfil_ativo_id || !atendimento.value?.cidadao) return null
  
  const perfis = atendimento.value.cidadao.perfis_profissionais
  if (!perfis) return null
  
  return perfis.find(p => p.id === atendimento.value!.perfil_ativo_id)
})

// Status disponíveis
const statusDisponiveis: { value: StatusAtendimento; label: string }[] = [
  { value: 'aberto', label: 'Aberto' },
  { value: 'em_andamento', label: 'Em Andamento' },
  { value: 'aguardando_terceiros', label: 'Aguardando Terceiros' },
  { value: 'concluido', label: 'Concluído' }
]

const podeAlterarStatus = computed(() => authStore.hasPermission(PERMS.atendStatus))

const statusEhAberto = computed(() => atendimento.value?.status === 'aberto')

const podeEditarDados = computed(() => {
  if (!atendimento.value) return false
  return authStore.hasPermission(PERMS.atendEdit) && statusEhAberto.value
})

const podeRegistrarDespacho = computed(() => authStore.hasPermission(PERMS.atendEdit))

const podeReatribuir = computed(() => authStore.hasPermission(PERMS.atendReassign))

const responsaveisParaReatribuir = computed(() => {
  const lista = atendimentosStore.responsaveisElegiveis
  if (!atendimento.value) return lista
  return lista.filter(u => u.id !== atendimento.value!.responsavelId)
})

const podeExcluir = computed(() => {
  if (!atendimento.value) return false
  return authStore.hasPermission(PERMS.atendDelete) && statusEhAberto.value
})

const statusOpcoes = computed(() => {
  if (statusEhAberto.value) {
    return statusDisponiveis
  }
  return statusDisponiveis.filter(s => s.value !== 'aberto')
})

const anexosAbertura = computed(() => atendimento.value?.anexos ?? [])

const formatarTamanho = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const baixarAnexo = async (anexo: Atendimento['anexos'][number]) => {
  try {
    await atendimentosStore.downloadAnexoAtendimento(anexo)
  } catch {
    await showError('Não foi possível baixar o arquivo.')
  }
}

watch(
  () => atendimentosStore.atendimentos.find(a => a.id === route.params.id),
  (found) => {
    if (found) {
      atendimento.value = found
    }
  },
  { deep: true },
)

// Carregar dados
onMounted(async () => {
  const id = route.params.id as string
  await Promise.all([
    atendimentosStore.fetchResponsaveisElegiveis().catch(() => []),
    atendimentosStore.getAtendimentoById(id).then(a => {
      atendimento.value = a
    }),
  ])

  if (!atendimento.value) {
    router.push('/atendimentos')
  }

  loading.value = false
})

// Handlers
const voltar = () => {
  router.push('/atendimentos')
}

const verCidadao = () => {
  if (atendimento.value) {
    router.push(`/crm/${atendimento.value.cidadaoId}`)
  }
}

const handleMudarStatus = async (novoStatus: StatusAtendimento) => {
  if (!atendimento.value || !podeAlterarStatus.value) return
  if (atendimento.value.status === novoStatus) return

  if (novoStatus === 'aberto' && atendimento.value.status !== 'aberto') {
    await showError('Não é permitido retornar um atendimento para o status Aberto.')
    statusSelectKey.value += 1
    return
  }

  if (atendimento.value.status === 'aberto' && novoStatus !== 'aberto') {
    const confirmed = await showConfirm(MENSAGEM_SAIR_STATUS_ABERTO, TITULO_SAIR_STATUS_ABERTO)
    if (!confirmed) {
      statusSelectKey.value += 1
      return
    }
  }

  alterandoStatus.value = true

  try {
    const ok = await atendimentosStore.updateStatus(atendimento.value.id, novoStatus)
    if (!ok) {
      await showError('Não foi possível alterar o status.')
      statusSelectKey.value += 1
      return
    }
    atendimento.value = await atendimentosStore.getAtendimentoById(atendimento.value.id)
  } finally {
    alterandoStatus.value = false
  }
}

const handleEditado = (atualizado?: Atendimento) => {
  if (atualizado) {
    atendimento.value = atualizado
  }
  mostrarModalEditar.value = false
}

const handleAtendimentoAtualizado = (atualizado: Atendimento) => {
  atendimento.value = atualizado
}

const handleReatribuir = async (novoResponsavelId: string) => {
  if (!atendimento.value || !podeReatribuir.value) return
  if (!novoResponsavelId || atendimento.value.responsavelId === novoResponsavelId) return

  alterandoStatus.value = true

  try {
    const ok = await atendimentosStore.reatribuirResponsavel(atendimento.value.id, novoResponsavelId)
    if (!ok) {
      await showError('Não foi possível reatribuir. Selecione um responsável válido.')
      return
    }
    atendimento.value = await atendimentosStore.getAtendimentoById(atendimento.value.id)
  } finally {
    alterandoStatus.value = false
  }
}

const handleExcluir = async () => {
  if (!atendimento.value || !podeExcluir.value) return

  const confirmed = await showConfirm(
    `Tem certeza que deseja excluir o atendimento #${atendimento.value.protocolo}? Esta ação não pode ser desfeita.`,
    'Excluir Atendimento'
  )

  if (!confirmed) return

  loading.value = true

  try {
    const sucesso = await atendimentosStore.deleteAtendimento(atendimento.value.id)
    
    if (sucesso) {
      showSuccess('Atendimento excluído com sucesso!')
      router.push('/atendimentos')
    } else {
      showError('Erro ao excluir atendimento.')
    }
  } catch (error) {
    showError('Erro ao excluir atendimento.')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <!-- Conteúdo -->
    <template v-else-if="atendimento">
      <!-- Header -->
      <div class="flex items-center justify-between gap-4">
        <div class="flex items-center gap-4">
          <button
            @click="voltar"
            class="p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-lg transition-colors text-gray-900 dark:text-slate-100"
          >
            <ArrowLeft class="w-5 h-5" />
          </button>
          <div>
            <h2 class="text-2xl font-bold text-gray-900 dark:text-slate-100">
              Protocolo #{{ atendimento.protocolo }}
            </h2>
            <RastreabilidadeMeta
              :rastreabilidade="atendimento.rastreabilidade"
              :alvo-auditoria="AUDITORIA_ALVO.atendimento(atendimento.id)"
              historico-titulo="Histórico do atendimento"
              show-criacao
              class="mt-1"
            />
            <p
              v-if="!atendimento.rastreabilidade?.ultimaAcaoEm && !atendimento.rastreabilidade?.criadoEm"
              class="text-sm text-gray-600 dark:text-slate-400 mt-1"
            >
              Aberto em {{ formatDate(atendimento.createdAt, true) }}
            </p>
          </div>
        </div>

        <div v-if="podeEditarDados || podeExcluir" class="flex items-center gap-2">
          <button
            v-if="podeEditarDados"
            type="button"
            @click="mostrarModalEditar = true"
            class="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors"
          >
            <Pencil class="w-5 h-5" />
            Editar
          </button>
          <button
            v-if="podeExcluir"
            type="button"
            @click="handleExcluir"
            class="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors"
          >
            <Trash2 class="w-5 h-5" />
            Excluir
          </button>
        </div>
      </div>

      <AtendimentoModal
        v-if="atendimento && podeEditarDados"
        v-model="mostrarModalEditar"
        :atendimento="atendimento"
        @success="handleEditado"
      />

      <!-- Layout Split -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Lado Esquerdo: Dados do Ticket -->
        <div class="lg:col-span-1 min-w-0">
          <div class="card space-y-6 sticky top-6">
            <!-- Status -->
            <div>
              <label class="text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wide block mb-2">
                Status
              </label>
              
              <select
                v-if="podeAlterarStatus"
                :key="statusSelectKey"
                :value="atendimento.status"
                @change="(e) => handleMudarStatus((e.target as HTMLSelectElement).value as StatusAtendimento)"
                :disabled="alterandoStatus"
                class="input"
              >
                <option
                  v-for="status in statusOpcoes"
                  :key="status.value"
                  :value="status.value"
                >
                  {{ status.label }}
                </option>
              </select>
              <Badge v-else :status="atendimento.status" />

              <p v-if="!podeAlterarStatus" class="text-xs text-gray-500 dark:text-slate-400 mt-1">
                Seu perfil pode visualizar o status, mas não alterá-lo.
              </p>
              <p
                v-else-if="!statusEhAberto"
                class="text-xs text-amber-700 dark:text-amber-400 mt-1"
              >
                Este protocolo não pode voltar para «Aberto» nem ter os dados do registro editados.
              </p>
              <p
                v-else
                class="text-xs text-gray-500 dark:text-slate-400 mt-1"
              >
                Ao sair de «Aberto», não será possível reverter nem editar os dados do registro.
              </p>
            </div>

            <!-- SLA -->
            <div
              v-if="atendimento.status === 'concluido'"
              class="flex items-center gap-2 p-3 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg"
            >
              <CheckCircle class="w-5 h-5 text-gray-500 dark:text-slate-400" />
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900 dark:text-slate-100">Atendimento concluído</p>
                <p class="text-xs text-gray-600 dark:text-slate-400">SLA não se aplica</p>
              </div>
            </div>

            <div
              v-else-if="atendimento.slaAtrasado"
              class="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg"
            >
              <AlertCircle class="w-5 h-5 text-red-600" />
              <div class="flex-1">
                <p class="text-sm font-medium text-red-900">SLA Atrasado</p>
                <p class="text-xs text-red-700">Venceu em {{ formatDate(atendimento.slaVencimento) }}</p>
              </div>
            </div>

            <div
              v-else
              class="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg"
            >
              <CheckCircle class="w-5 h-5 text-green-600" />
              <div class="flex-1">
                <p class="text-sm font-medium text-green-900">Dentro do Prazo</p>
                <p class="text-xs text-green-700">Vence em {{ formatDate(atendimento.slaVencimento) }}</p>
                <p
                  v-if="atendimento.slaHoras"
                  class="text-xs text-green-600/80 mt-1"
                >
                  Prazo: {{ atendimento.slaHoras }}h após abertura (prioridade {{ atendimento.prioridade }}).
                </p>
              </div>
            </div>

            <!-- Anexos da abertura -->
            <div>
              <label class="text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wide block mb-2">
                Anexos do registro
              </label>
              <ul v-if="anexosAbertura.length > 0" class="space-y-2">
                <li
                  v-for="anexo in anexosAbertura"
                  :key="anexo.id"
                  class="flex items-center gap-2 p-2 rounded-lg bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700"
                >
                  <Paperclip class="w-4 h-4 text-gray-500 flex-shrink-0" />
                  <button
                    type="button"
                    class="text-primary-600 dark:text-primary-400 hover:underline truncate text-left text-sm flex-1"
                    @click="baixarAnexo(anexo)"
                  >
                    {{ anexo.nome }}
                  </button>
                  <span class="text-xs text-gray-500 flex-shrink-0">{{ formatarTamanho(anexo.tamanho) }}</span>
                </li>
              </ul>
              <p v-else class="text-sm text-gray-500 dark:text-slate-400">
                Nenhum anexo na abertura deste atendimento.
              </p>
            </div>

            <!-- Assunto -->
            <div>
              <label class="text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wide block mb-2">
                Assunto
              </label>
              <p class="text-gray-900 dark:text-slate-100 font-medium">{{ atendimento.assunto }}</p>
            </div>

            <!-- Descrição -->
            <div>
              <label class="text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wide block mb-2">
                Descrição
              </label>
              <p class="text-gray-700 dark:text-slate-300 whitespace-pre-line">{{ atendimento.descricao }}</p>
            </div>

            <!-- Macrotema -->
            <div>
              <label class="text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wide block mb-2">
                Macrotema
              </label>
              <span
                :style="{
                  backgroundColor: atendimento.macrotema.cor + '20',
                  color: atendimento.macrotema.cor,
                  borderColor: atendimento.macrotema.cor + '40'
                }"
                class="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-medium border"
              >
                {{ atendimento.macrotema.nome }}
              </span>
            </div>

            <!-- Cidadão -->
            <div>
              <label class="text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wide block mb-2">
                Solicitante
              </label>
              <button
                @click="verCidadao"
                class="flex items-center gap-3 w-full p-3 bg-gray-50 dark:bg-slate-800 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg transition-colors text-left"
              >
                <Avatar :nome="atendimento.cidadao.nome" tamanho="md" />
                <div class="flex-1 min-w-0">
                  <p class="font-medium text-gray-900 dark:text-slate-100 truncate">{{ atendimento.cidadao.nome }}</p>
                  <p class="text-sm text-gray-600 dark:text-slate-400">{{ atendimento.cidadao.telefone }}</p>
                  <p v-if="perfilAtivo" class="text-xs text-gray-500 dark:text-slate-500 italic mt-1">
                    Atuando como: {{ perfilAtivo.cargo }} - {{ perfilAtivo.instituicao }}
                  </p>
                </div>
              </button>
            </div>

            <!-- Responsável -->
            <div>
              <label class="text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wide block mb-2">
                Responsável
              </label>
              <div class="flex items-center gap-3 mb-2">
                <Avatar :nome="atendimento.responsavel.nome" tamanho="md" />
                <div class="flex-1">
                  <p class="font-medium text-gray-900 dark:text-slate-100">{{ atendimento.responsavel.nome }}</p>
                  <p class="text-sm text-gray-600 dark:text-slate-400">{{ atendimento.responsavel.cargo }}</p>
                </div>
              </div>
              
              <select
                v-if="podeReatribuir && responsaveisParaReatribuir.length > 0"
                :value="atendimento.responsavelId"
                @change="(e) => handleReatribuir((e.target as HTMLSelectElement).value)"
                :disabled="alterandoStatus"
                class="input text-sm"
              >
                <option :value="atendimento.responsavelId" disabled>
                  {{ atendimento.responsavel.nome }} (atual)
                </option>
                <option
                  v-for="usuario in responsaveisParaReatribuir"
                  :key="usuario.id"
                  :value="usuario.id"
                >
                  {{ usuario.nome }} — {{ usuario.cargo }}
                </option>
              </select>
              <p
                v-if="podeReatribuir"
                class="text-xs text-gray-500 dark:text-slate-400 mt-1"
              >
                A reatribuição gerará um despacho automático
              </p>
            </div>

            <!-- Prioridade -->
            <div>
              <label class="text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wide block mb-2">
                Prioridade
              </label>
              <span
                :class="{
                  'bg-green-100 text-green-700 border-green-200': atendimento.prioridade === 'baixa',
                  'bg-blue-100 text-blue-700 border-blue-200': atendimento.prioridade === 'media',
                  'bg-orange-100 text-orange-700 border-orange-200': atendimento.prioridade === 'alta',
                  'bg-red-100 text-red-700 border-red-200': atendimento.prioridade === 'urgente'
                }"
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border capitalize"
              >
                {{ atendimento.prioridade }}
              </span>
            </div>
          </div>
        </div>

        <!-- Lado Direito: Timeline de Despachos -->
        <div class="lg:col-span-2 min-w-0">
          <div class="card h-[calc(100vh-200px)] flex flex-col overflow-hidden">
            <div class="mb-4 pb-4 border-b border-gray-200 dark:border-slate-700 flex-shrink-0">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-slate-100">
                Timeline de Despachos
              </h3>
              <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
                {{ atendimento.despachos.length }} {{ atendimento.despachos.length === 1 ? 'despacho' : 'despachos' }}
              </p>
            </div>

            <div class="flex-1 min-h-0 overflow-hidden">
              <DespachosTimeline
                :atendimento-id="atendimento.id"
                :despachos="atendimento.despachos"
                :pode-registrar-despacho="podeRegistrarDespacho"
                @updated="handleAtendimentoAtualizado"
              />
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
