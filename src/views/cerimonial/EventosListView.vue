<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCerimonialStore } from '@/stores/cerimonial'
import { useAlertDialog } from '@/composables/useAlertDialog'
import RastreabilidadeMeta from '@/components/common/RastreabilidadeMeta.vue'
import { AUDITORIA_ALVO } from '@/services/auditoria'
import {
  Sparkles,
  Calendar,
  MapPin,
  Users,
  Search,
  Eye,
  Filter,
  Plus,
  X
} from 'lucide-vue-next'

const router = useRouter()
const cerimonialStore = useCerimonialStore()
const { showWarning, showError } = useAlertDialog()

const busca = ref('')
const filtroStatus = ref<string>('todos')
const mostrarModal = ref(false)
const loading = ref(false)

// Form novo evento
const novoEvento = ref({
  titulo: '',
  tipo: 'cerimonial' as 'cerimonial' | 'audiencia' | 'sessao' | 'reuniao',
  data: '',
  horaInicio: '',
  horaFim: '',
  local: '',
  descricao: '',
  totalConvidados: 0
})

onMounted(async () => {
  await cerimonialStore.initialize()
})

const eventosFiltrados = computed(() => {
  let eventos = cerimonialStore.eventos

  // Filtrar por busca
  if (busca.value.trim()) {
    const query = busca.value.toLowerCase()
    eventos = eventos.filter(e =>
      e.titulo.toLowerCase().includes(query) ||
      e.local.toLowerCase().includes(query)
    )
  }

  // Filtrar por status
  if (filtroStatus.value !== 'todos') {
    eventos = eventos.filter(e => e.status === filtroStatus.value)
  }

  return eventos.sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime())
})

function visualizarEvento(eventoId: string) {
  router.push(`/eventos/${eventoId}`)
}

function formatarData(data: string) {
  return new Date(data).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  })
}

function getStatusLabel(status: string) {
  const labels: Record<string, string> = {
    planejamento: 'Planejamento',
    confirmado: 'Confirmado',
    em_andamento: 'Em Andamento',
    concluido: 'Concluído',
    cancelado: 'Cancelado'
  }
  return labels[status] || status
}

function getStatusColor(status: string) {
  const colors: Record<string, string> = {
    planejamento: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
    confirmado: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    em_andamento: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
    concluido: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
    cancelado: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
  }
  return colors[status] || 'bg-gray-100 text-gray-700'
}

const estatisticas = computed(() => {
  const total = cerimonialStore.eventos.length
  const confirmados = cerimonialStore.eventos.filter(e => e.status === 'confirmado').length
  const planejamento = cerimonialStore.eventos.filter(e => e.status === 'planejamento').length
  
  return { total, confirmados, planejamento }
})

function abrirModal() {
  mostrarModal.value = true
}

function fecharModal() {
  mostrarModal.value = false
  resetForm()
}

function resetForm() {
  novoEvento.value = {
    titulo: '',
    tipo: 'cerimonial',
    data: '',
    horaInicio: '',
    horaFim: '',
    local: '',
    descricao: '',
    totalConvidados: 0
  }
}

async function criarEvento() {
  if (!novoEvento.value.titulo || !novoEvento.value.data || !novoEvento.value.horaInicio || !novoEvento.value.local) {
    await showWarning('Preencha título, data, hora de início e local.', 'Campos obrigatórios')
    return
  }

  loading.value = true

  try {
    const evento = await cerimonialStore.criarEvento({
      ...novoEvento.value,
      status: 'planejamento'
    })

    fecharModal()
    
    // Redirecionar para o dashboard do evento
    if (evento) {
      router.push(`/eventos/${evento.id}`)
    }
  } catch (error) {
    console.error('Erro ao criar evento:', error)
    await showError('Não foi possível criar o evento. Tente novamente.', 'Erro ao criar evento')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
          <Sparkles class="w-7 h-7 text-primary-600 dark:text-primary-400" />
          Eventos & Cerimonial
        </h1>
        <p class="text-gray-600 dark:text-gray-400 mt-1">
          Gestão completa de eventos institucionais e cerimoniais
        </p>
      </div>

      <!-- Botão Novo Evento -->
      <button
        @click="abrirModal"
        class="flex items-center gap-2 px-5 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
      >
        <Plus class="w-5 h-5" />
        Novo Evento
      </button>
    </div>

    <!-- Cards de Estatísticas -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-900/30 rounded-lg border border-primary-200 dark:border-primary-800 p-4">
        <div class="flex items-center gap-3">
          <div class="p-3 bg-primary-500 dark:bg-primary-600 rounded-lg">
            <Sparkles class="w-6 h-6 text-white" />
          </div>
          <div>
            <p class="text-2xl font-bold text-primary-900 dark:text-primary-100">
              {{ estatisticas.total }}
            </p>
            <p class="text-sm text-primary-700 dark:text-primary-300">Total de Eventos</p>
          </div>
        </div>
      </div>

      <div class="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-900/30 rounded-lg border border-green-200 dark:border-green-800 p-4">
        <div class="flex items-center gap-3">
          <div class="p-3 bg-green-500 dark:bg-green-600 rounded-lg">
            <Calendar class="w-6 h-6 text-white" />
          </div>
          <div>
            <p class="text-2xl font-bold text-green-900 dark:text-green-100">
              {{ estatisticas.confirmados }}
            </p>
            <p class="text-sm text-green-700 dark:text-green-300">Confirmados</p>
          </div>
        </div>
      </div>

      <div class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-900/30 rounded-lg border border-blue-200 dark:border-blue-800 p-4">
        <div class="flex items-center gap-3">
          <div class="p-3 bg-blue-500 dark:bg-blue-600 rounded-lg">
            <Users class="w-6 h-6 text-white" />
          </div>
          <div>
            <p class="text-2xl font-bold text-blue-900 dark:text-blue-100">
              {{ estatisticas.planejamento }}
            </p>
            <p class="text-sm text-blue-700 dark:text-blue-300">Em Planejamento</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Filtros e Busca -->
    <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <!-- Busca -->
        <div class="flex-1 relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            v-model="busca"
            type="text"
            placeholder="Buscar eventos..."
            class="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400"
          />
        </div>

        <!-- Filtro de Status -->
        <div class="flex items-center gap-2">
          <Filter class="w-5 h-5 text-gray-400 flex-shrink-0" />
          <select
            v-model="filtroStatus"
            class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400"
          >
            <option value="todos">Todos os Status</option>
            <option value="planejamento">Planejamento</option>
            <option value="confirmado">Confirmado</option>
            <option value="em_andamento">Em Andamento</option>
            <option value="concluido">Concluído</option>
            <option value="cancelado">Cancelado</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Tabela de Eventos -->
    <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 dark:bg-gray-700/50 border-b border-gray-200 dark:border-gray-600">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Data
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Evento
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Local
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Convidados
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Ações
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-600">
            <tr
              v-for="evento in eventosFiltrados"
              :key="evento.id"
              @click="visualizarEvento(evento.id)"
              class="hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2 text-sm text-gray-900 dark:text-gray-100">
                  <Calendar class="w-4 h-4 text-gray-400" />
                  {{ formatarData(evento.data) }}
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {{ evento.horaInicio }} - {{ evento.horaFim }}
                </div>
              </td>
              
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {{ evento.titulo }}
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400 mt-1 uppercase">
                  {{ evento.tipo }}
                </div>
                <RastreabilidadeMeta
                  :rastreabilidade="evento.rastreabilidade"
                  :alvo-auditoria="AUDITORIA_ALVO.eventoCerimonial(evento.id)"
                  historico-titulo="Histórico do evento"
                  compact
                  class="mt-2"
                  @click.stop
                />
              </td>
              
              <td class="px-6 py-4">
                <div class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                  <MapPin class="w-4 h-4" />
                  {{ evento.local }}
                </div>
              </td>
              
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2 text-sm text-gray-900 dark:text-gray-100">
                  <Users class="w-4 h-4 text-gray-400" />
                  {{ evento.totalConvidados }}
                </div>
              </td>
              
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    getStatusColor(evento.status),
                    'px-2.5 py-1 rounded-full text-xs font-medium'
                  ]"
                >
                  {{ getStatusLabel(evento.status) }}
                </span>
              </td>
              
              <td class="px-6 py-4 whitespace-nowrap text-right">
                <button
                  @click.stop="visualizarEvento(evento.id)"
                  class="inline-flex items-center gap-1 px-3 py-1.5 text-sm bg-primary-100 hover:bg-primary-200 dark:bg-primary-900/30 dark:hover:bg-primary-900/50 text-primary-700 dark:text-primary-400 rounded-lg font-medium transition-colors"
                >
                  <Eye class="w-4 h-4" />
                  Ver Dashboard
                </button>
              </td>
            </tr>

            <!-- Estado Vazio -->
            <tr v-if="eventosFiltrados.length === 0">
              <td colspan="6" class="px-6 py-16 text-center">
                <Sparkles class="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
                <p class="text-gray-500 dark:text-gray-400">
                  {{ busca ? 'Nenhum evento encontrado' : 'Nenhum evento cadastrado' }}
                </p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal Novo Evento -->
    <div
      v-if="mostrarModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
      @click.self="fecharModal"
    >
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <!-- Header Modal -->
        <div class="sticky top-0 bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4 flex items-center justify-between">
          <h2 class="text-xl font-bold text-white">Criar Novo Evento</h2>
          <button
            @click="fecharModal"
            class="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
          >
            <X class="w-5 h-5" />
          </button>
        </div>

        <!-- Formulário -->
        <form @submit.prevent="criarEvento" class="p-6 space-y-5">
          <!-- Título -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Título do Evento *
            </label>
            <input
              v-model="novoEvento.titulo"
              type="text"
              required
              placeholder="Ex: Sessão Solene de Entrega de Títulos"
              class="w-full px-4 py-3 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-gray-900 dark:text-white"
            />
          </div>

          <!-- Tipo -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Tipo de Evento *
            </label>
            <select
              v-model="novoEvento.tipo"
              required
              class="w-full px-4 py-3 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-gray-900 dark:text-white"
            >
              <option value="cerimonial">Cerimonial</option>
              <option value="audiencia">Audiência Pública</option>
              <option value="sessao">Sessão</option>
              <option value="reuniao">Reunião</option>
            </select>
          </div>

          <!-- Data e Horas -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Data *
              </label>
              <input
                v-model="novoEvento.data"
                type="date"
                required
                class="w-full px-4 py-3 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-gray-900 dark:text-white"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Hora Início *
              </label>
              <input
                v-model="novoEvento.horaInicio"
                type="time"
                required
                class="w-full px-4 py-3 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-gray-900 dark:text-white"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Hora Fim
              </label>
              <input
                v-model="novoEvento.horaFim"
                type="time"
                class="w-full px-4 py-3 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-gray-900 dark:text-white"
              />
            </div>
          </div>

          <!-- Local -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Local *
            </label>
            <input
              v-model="novoEvento.local"
              type="text"
              required
              placeholder="Ex: Plenário da Câmara Municipal"
              class="w-full px-4 py-3 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-gray-900 dark:text-white"
            />
          </div>

          <!-- Descrição -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Descrição
            </label>
            <textarea
              v-model="novoEvento.descricao"
              rows="3"
              placeholder="Breve descrição do evento..."
              class="w-full px-4 py-3 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-gray-900 dark:text-white resize-none"
            ></textarea>
          </div>

          <!-- Total Convidados -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Total de Convidados Estimado
            </label>
            <input
              v-model.number="novoEvento.totalConvidados"
              type="number"
              min="0"
              placeholder="0"
              class="w-full px-4 py-3 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-gray-900 dark:text-white"
            />
          </div>

          <!-- Botões -->
          <div class="flex items-center gap-3 pt-4">
            <button
              type="submit"
              :disabled="loading"
              class="flex-1 px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
            >
              <span v-if="loading">A criar...</span>
              <span v-else>Criar Evento</span>
            </button>

            <button
              type="button"
              @click="fecharModal"
              class="px-4 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 font-medium rounded-lg transition-all"
            >
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
