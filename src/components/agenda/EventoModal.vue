<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useAgendaStore } from '@/stores/agenda'
import { useCrmStore } from '@/stores/crm'
import { useAuthStore } from '@/stores/auth'
import { PERMS } from '@/constants/rbac'
import { useAlertDialog } from '@/composables/useAlertDialog'
import { ApiError } from '@/services/api'
import { getAgendaApiErrorMessage } from '@/stores/agenda'
import type { ConvidadoEventoResumo, Evento } from '@/stores/agenda'
import type { Cidadao } from '@/types'
import Modal from '@/components/common/Modal.vue'
import Button from '@/components/common/Button.vue'
import RastreabilidadeMeta from '@/components/common/RastreabilidadeMeta.vue'
import { AUDITORIA_ALVO } from '@/services/auditoria'
import { AlertCircle, Users, MapPin, X, Search, Tag, Trash2 } from 'lucide-vue-next'

interface Props {
  modelValue: boolean
  evento?: Evento | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'saved': []
  'deleted': []
}>()

const agendaStore = useAgendaStore()
const crmStore = useCrmStore()
const authStore = useAuthStore()
const { showConfirm, showSuccess, showError } = useAlertDialog()

// Form
const form = ref({
  titulo: '',
  descricao: '',
  tipoId: '',
  data: '',
  horaInicio: '',
  horaFim: '',
  espacoId: '',
  convidadosIds: [] as string[],
  status: 'agendado' as 'agendado' | 'realizado' | 'cancelado',
  isSyncedGoogle: false,
  isSyncedOutlook: false
})

const buscaConvidado = ref('')
const erro = ref('')
const convidadosBusca = ref<Cidadao[]>([])
const buscandoConvidados = ref(false)
const erroBuscaConvidados = ref('')
const convidadosPorId = ref<Record<string, Cidadao>>({})
let buscaConvidadoTimer: ReturnType<typeof setTimeout> | null = null
let buscaConvidadosSeq = 0

function cacheConvidadoResumo(c: ConvidadoEventoResumo) {
  convidadosPorId.value[c.id] = {
    id: c.id,
    nome: c.nome,
    cpf: c.cpf,
    email: c.email,
    avatar: c.avatar,
    telefone: c.telefone ?? '',
    createdAt: '',
    updatedAt: '',
  }
}

function cacheConvidado(c: Cidadao) {
  convidadosPorId.value[c.id] = c
}

// Computed
const titulo = computed(() => props.evento ? 'Editar Evento' : 'Novo Evento')

// Pode excluir: apenas se tem permissão e está editando (não é novo evento)
const podeExcluir = computed(() => {
  return props.evento && authStore.hasPermission(PERMS.agendaDelete)
})

const convidadosSelecionados = computed(() => {
  return form.value.convidadosIds
    .map(id =>
      convidadosPorId.value[id]
      ?? crmStore.cidadaos.find(c => c.id === id),
    )
    .filter(Boolean) as Cidadao[]
})

const convidadosFiltrados = computed(() =>
  convidadosBusca.value.filter(c => !form.value.convidadosIds.includes(c.id)),
)

watch(buscaConvidado, (query) => {
  if (buscaConvidadoTimer) {
    clearTimeout(buscaConvidadoTimer)
  }
  const trimmed = query.trim()
  if (trimmed.length < 2) {
    convidadosBusca.value = []
    buscandoConvidados.value = false
    erroBuscaConvidados.value = ''
    return
  }
  buscandoConvidados.value = true
  erroBuscaConvidados.value = ''
  const seq = ++buscaConvidadosSeq
  buscaConvidadoTimer = setTimeout(async () => {
    try {
      const result = await crmStore.searchCidadaos(trimmed)
      if (seq !== buscaConvidadosSeq) return
      convidadosBusca.value = result
    } catch (e) {
      if (seq !== buscaConvidadosSeq) return
      convidadosBusca.value = []
      if (e instanceof ApiError) {
        if (e.status === 401) {
          erroBuscaConvidados.value = 'Sessão expirada. Faça login novamente.'
        } else if (e.status === 403) {
          erroBuscaConvidados.value = 'Sem permissão para consultar cidadãos no CRM.'
        } else {
          erroBuscaConvidados.value = 'Erro ao buscar cidadãos. Tente novamente.'
        }
      } else {
        erroBuscaConvidados.value = 'Erro ao buscar cidadãos. Tente novamente.'
      }
    } finally {
      if (seq === buscaConvidadosSeq) {
        buscandoConvidados.value = false
      }
    }
  }, 300)
})

const espacoSelecionado = computed(() => {
  if (!form.value.espacoId) return null
  return agendaStore.getEspacoById(form.value.espacoId)
})

// Detecção de conflito em tempo real
const conflito = computed(() => {
  if (!form.value.espacoId || !form.value.data || !form.value.horaInicio || !form.value.horaFim) {
    return { hasConflict: false }
  }

  return agendaStore.checkConflict(
    form.value.espacoId,
    form.value.data,
    form.value.horaInicio,
    form.value.horaFim,
    props.evento?.id
  )
})

// Watchers
watch(() => props.modelValue, (value) => {
  if (value) {
    if (props.evento) {
      // Edição
      form.value = {
        titulo: props.evento.titulo,
        descricao: props.evento.descricao || '',
        tipoId: props.evento.tipoId,
        data: props.evento.data,
        horaInicio: props.evento.horaInicio,
        horaFim: props.evento.horaFim,
        espacoId: props.evento.espacoId || '',
        convidadosIds: [...props.evento.convidadosIds],
        status: props.evento.status,
        isSyncedGoogle: props.evento.isSyncedGoogle || false,
        isSyncedOutlook: props.evento.isSyncedOutlook || false
      }
    } else {
      // Novo evento - verificar se há data/hora no localStorage (vindo do calendário)
      const dataCalendario = localStorage.getItem('novoEventoData')
      const horaCalendario = localStorage.getItem('novoEventoHora')
      
      const hoje = dataCalendario || new Date().toISOString().split('T')[0]
      const horaInicio = horaCalendario || '09:00'
      
      // Calcular hora fim (1 hora depois)
      const [h, m] = horaInicio.split(':').map(Number)
      const horaFim = `${String(h + 1).padStart(2, '0')}:${String(m).padStart(2, '0')}`
      
      const primeiroTipo = agendaStore.tiposEventoAtivos[0]
      form.value = {
        titulo: '',
        descricao: '',
        tipoId: primeiroTipo?.id || '',
        data: hoje,
        horaInicio: horaInicio,
        horaFim: horaFim,
        espacoId: '',
        convidadosIds: [],
        status: 'agendado',
        isSyncedGoogle: false,
        isSyncedOutlook: false
      }
      
      // Limpar localStorage após usar
      localStorage.removeItem('novoEventoData')
      localStorage.removeItem('novoEventoHora')
    }
    erro.value = ''
    erroBuscaConvidados.value = ''
    buscaConvidado.value = ''
    convidadosBusca.value = []
    convidadosPorId.value = {}
    props.evento?.convidadosResumo?.forEach(cacheConvidadoResumo)
  }
})

// Methods
const adicionarConvidado = (cidadao: Cidadao) => {
  cacheConvidado(cidadao)
  if (!form.value.convidadosIds.includes(cidadao.id)) {
    form.value.convidadosIds.push(cidadao.id)
  }
  buscaConvidado.value = ''
  convidadosBusca.value = []
}

const removerConvidado = (cidadaoId: string) => {
  const index = form.value.convidadosIds.indexOf(cidadaoId)
  if (index > -1) {
    form.value.convidadosIds.splice(index, 1)
  }
}

const validarFormulario = (): boolean => {
  if (!form.value.titulo.trim()) {
    erro.value = 'O título é obrigatório'
    return false
  }

  if (!form.value.data) {
    erro.value = 'A data é obrigatória'
    return false
  }

  if (!form.value.horaInicio || !form.value.horaFim) {
    erro.value = 'Os horários são obrigatórios'
    return false
  }

  if (form.value.horaInicio >= form.value.horaFim) {
    erro.value = 'A hora de término deve ser posterior à hora de início'
    return false
  }

  if (conflito.value.hasConflict) {
    erro.value = 'Existe um conflito de horário com outro evento neste espaço'
    return false
  }

  return true
}

const salvar = async () => {
  if (!validarFormulario()) return

  try {
    const payload = {
      titulo: form.value.titulo,
      descricao: form.value.descricao,
      tipoId: form.value.tipoId,
      data: form.value.data,
      horaInicio: form.value.horaInicio,
      horaFim: form.value.horaFim,
      espacoId: form.value.espacoId || undefined,
      convidadosIds: form.value.convidadosIds,
      status: form.value.status,
      isSyncedGoogle: form.value.isSyncedGoogle,
      isSyncedOutlook: form.value.isSyncedOutlook,
      criadoPor: props.evento?.criadoPor ?? authStore.usuario?.nome ?? '—',
    }

    if (props.evento) {
      await agendaStore.updateEvento(props.evento.id, payload)
    } else {
      await agendaStore.createEvento(payload)
    }

    showSuccess(props.evento ? 'Evento atualizado!' : 'Evento criado!')
    emit('saved')
    fechar()
  } catch (error) {
    const msg = getAgendaApiErrorMessage(error)
    erro.value = msg
    if (error instanceof ApiError && error.status === 400) {
      showError(msg)
    } else {
      showError('Erro ao salvar evento.')
    }
  }
}

const handleExcluir = async () => {
  if (!props.evento || !podeExcluir.value) return

  const confirmed = await showConfirm(
    `Tem certeza que deseja excluir o evento "${props.evento.titulo}"? Esta ação não pode ser desfeita.`,
    'Excluir Evento'
  )

  if (!confirmed) return

  try {
    const sucesso = await agendaStore.deleteEvento(props.evento.id)
    
    if (sucesso) {
      showSuccess('Evento excluído com sucesso!')
      emit('deleted')
      fechar()
    } else {
      showError('Erro ao excluir evento.')
    }
  } catch (error) {
    showError('Erro ao excluir evento.')
    console.error(error)
  }
}

const fechar = () => {
  emit('update:modelValue', false)
}

const getTipoNome = (tipoId: string) => {
  const tipo = agendaStore.getTipoEventoById(tipoId)
  return tipo?.nome || 'Desconhecido'
}

const getTipoCor = (tipoId: string) => {
  const tipo = agendaStore.getTipoEventoById(tipoId)
  return tipo?.cor || '#6b7280'
}
</script>

<template>
  <Modal
    :model-value="modelValue"
    @update:model-value="fechar"
    :titulo="titulo"
    largura="lg"
  >
    <form @submit.prevent="salvar" class="space-y-5">
      <!-- Erro Geral -->
      <div v-if="erro" class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-2">
        <AlertCircle class="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
        <p class="text-sm text-red-900 dark:text-red-300">{{ erro }}</p>
      </div>

      <RastreabilidadeMeta
        v-if="props.evento"
        :rastreabilidade="props.evento.rastreabilidade"
        :alvo-auditoria="AUDITORIA_ALVO.eventoAgenda(props.evento.id)"
        historico-titulo="Histórico do compromisso"
        show-criacao
      />

      <!-- Título -->
      <div>
        <label class="label">Título do Evento *</label>
        <input
          v-model="form.titulo"
          type="text"
          class="input"
          placeholder="Ex: Reunião de Planejamento"
          required
        />
      </div>

      <!-- Tipo -->
      <div>
        <label class="label">Tipo de Evento *</label>
        <select v-model="form.tipoId" class="input" required>
          <option value="" disabled>Selecione um tipo</option>
          <option
            v-for="tipo in agendaStore.tiposEventoAtivos"
            :key="tipo.id"
            :value="tipo.id"
          >
            {{ tipo.nome }}
          </option>
        </select>
        
        <!-- Preview do Tipo Selecionado -->
        <div v-if="form.tipoId" class="mt-2 inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium" :style="{ backgroundColor: getTipoCor(form.tipoId) + '20', color: getTipoCor(form.tipoId) }">
          <Tag class="w-3 h-3" />
          {{ getTipoNome(form.tipoId) }}
        </div>
      </div>

      <!-- Data e Horários -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="label">Data *</label>
          <input
            v-model="form.data"
            type="date"
            class="input"
            required
          />
        </div>
        <div>
          <label class="label">Hora Início *</label>
          <input
            v-model="form.horaInicio"
            type="time"
            class="input"
            required
          />
        </div>
        <div>
          <label class="label">Hora Término *</label>
          <input
            v-model="form.horaFim"
            type="time"
            class="input"
            required
          />
        </div>
      </div>

      <!-- Espaço -->
      <div>
        <label class="label">
          <MapPin class="w-4 h-4 inline" />
          Reservar Espaço
        </label>
        <select v-model="form.espacoId" class="input">
          <option value="">Nenhum espaço (evento externo ou remoto)</option>
          <option
            v-for="espaco in agendaStore.espacosAtivos"
            :key="espaco.id"
            :value="espaco.id"
          >
            {{ espaco.nome }} (Capacidade: {{ espaco.capacidade }} pessoas)
          </option>
        </select>

        <!-- Info do Espaço Selecionado -->
        <div v-if="espacoSelecionado" class="mt-2 p-3 bg-gray-50 dark:bg-slate-900 rounded-lg">
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-700 dark:text-slate-300">
              <strong>{{ espacoSelecionado.nome }}</strong>
            </span>
            <span class="text-gray-500 dark:text-slate-400">
              {{ espacoSelecionado.capacidade }} pessoas
            </span>
          </div>
          <p v-if="espacoSelecionado.descricao" class="text-xs text-gray-500 dark:text-slate-400 mt-1">
            {{ espacoSelecionado.descricao }}
          </p>
        </div>

        <!-- Alerta de Conflito -->
        <div
          v-if="conflito.hasConflict && conflito.conflictingEvent"
          class="mt-2 p-3 bg-red-50 dark:bg-red-900/20 border-2 border-red-400 dark:border-red-600 rounded-lg animate-pulse"
        >
          <div class="flex items-start gap-2">
            <AlertCircle class="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <div class="flex-1">
              <p class="text-sm font-semibold text-red-900 dark:text-red-300">
                ⚠️ Este espaço já está reservado!
              </p>
              <p class="text-xs text-red-800 dark:text-red-400 mt-1">
                <strong>{{ conflito.conflictingEvent.titulo }}</strong><br>
                {{ conflito.conflictingEvent.horaInicio }} às {{ conflito.conflictingEvent.horaFim }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Convidados -->
      <div>
        <label class="label">
          <Users class="w-4 h-4 inline" />
          Convidados (Cidadãos do CRM)
        </label>
        
        <!-- Busca -->
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-slate-500" />
          <input
            v-model="buscaConvidado"
            type="text"
            class="input pl-10"
            placeholder="Digite ao menos 2 caracteres (nome, CPF ou e-mail)..."
          />
        </div>

        <p v-if="buscandoConvidados" class="text-xs text-gray-500 dark:text-slate-400 mt-2">
          Buscando no CRM…
        </p>
        <p
          v-else-if="erroBuscaConvidados"
          class="text-xs text-red-600 dark:text-red-400 mt-2"
        >
          {{ erroBuscaConvidados }}
        </p>
        <p
          v-else-if="buscaConvidado.trim().length >= 2 && convidadosFiltrados.length === 0"
          class="text-xs text-gray-500 dark:text-slate-400 mt-2"
        >
          Nenhum cidadão encontrado.
        </p>

        <!-- Lista de sugestões -->
        <div v-if="convidadosFiltrados.length > 0" class="mt-2 border border-gray-200 dark:border-slate-700 rounded-lg overflow-hidden bg-white dark:bg-slate-800 max-h-48 overflow-y-auto">
          <button
            v-for="cidadao in convidadosFiltrados"
            :key="cidadao.id"
            @click.prevent="adicionarConvidado(cidadao)"
            type="button"
            class="w-full px-3 py-2 text-left hover:bg-gray-50 dark:hover:bg-slate-700 transition-colors flex items-center gap-2"
          >
            <img
              v-if="cidadao.avatar"
              :src="cidadao.avatar"
              :alt="cidadao.nome"
              class="w-8 h-8 rounded-full"
            />
            <div
              v-else
              class="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-primary-700 dark:text-primary-300 font-semibold text-sm"
            >
              {{ cidadao.nome.charAt(0).toUpperCase() }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 dark:text-slate-100 truncate">
                {{ cidadao.nome }}
              </p>
              <p v-if="cidadao.cpf" class="text-xs text-gray-500 dark:text-slate-400">
                {{ cidadao.cpf }}
              </p>
            </div>
          </button>
        </div>

        <!-- Convidados selecionados -->
        <div v-if="convidadosSelecionados.length > 0" class="mt-3 flex flex-wrap gap-2">
          <div
            v-for="cidadao in convidadosSelecionados"
            :key="cidadao?.id"
            class="inline-flex items-center gap-2 px-3 py-1.5 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded-full text-sm"
          >
            <img
              v-if="cidadao?.avatar"
              :src="cidadao.avatar"
              :alt="cidadao.nome"
              class="w-5 h-5 rounded-full"
            />
            <div
              v-else
              class="w-5 h-5 rounded-full bg-primary-600 flex items-center justify-center text-white font-semibold text-xs"
            >
              {{ cidadao?.nome.charAt(0).toUpperCase() }}
            </div>
            <span>{{ cidadao?.nome }}</span>
            <button
              @click.prevent="removerConvidado(cidadao?.id || '')"
              type="button"
              class="hover:text-primary-900 dark:hover:text-primary-100"
            >
              <X class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      <!-- Descrição -->
      <div>
        <label class="label">Descrição / Observações</label>
        <textarea
          v-model="form.descricao"
          rows="3"
          class="input"
          placeholder="Detalhes adicionais sobre o evento..."
        ></textarea>
      </div>
    </form>

    <template #footer>
      <div class="flex items-center justify-between w-full">
        <!-- Botão Excluir (esquerda) -->
        <Button
          v-if="podeExcluir"
          variant="danger"
          @click="handleExcluir"
        >
          <template #icon>
            <Trash2 class="w-4 h-4" />
          </template>
          Excluir
        </Button>
        <div v-else></div>

        <!-- Botões Cancelar/Salvar (direita) -->
        <div class="flex gap-3">
          <Button variant="secondary" @click="fechar">
            Cancelar
          </Button>
          <Button
            variant="primary"
            @click="salvar"
            :disabled="!!conflito.hasConflict || !form.titulo.trim()"
          >
            {{ props.evento ? 'Salvar Alterações' : 'Criar Evento' }}
          </Button>
        </div>
      </div>
    </template>
  </Modal>
</template>
