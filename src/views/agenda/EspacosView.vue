<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAgendaStore } from '@/stores/agenda'
import type { Espaco } from '@/stores/agenda'
import Button from '@/components/common/Button.vue'
import Modal from '@/components/common/Modal.vue'
import RastreabilidadeMeta from '@/components/common/RastreabilidadeMeta.vue'
import { AUDITORIA_ALVO } from '@/services/auditoria'
import { 
  Plus, 
  Edit, 
  Trash2, 
  MapPin,
  Users,
  AlertCircle,
  Presentation,
  Building,
  Briefcase,
  Theater
} from 'lucide-vue-next'

const agendaStore = useAgendaStore()

// Estado
const mostrarModalEspaco = ref(false)
const espacoEditando = ref<Espaco | null>(null)
const confirmandoExclusao = ref<string | null>(null)
const erroExclusao = ref('')

// Form
const form = ref({
  nome: '',
  descricao: '',
  capacidade: 10,
  icone: 'presentation',
  cor: '#3b82f6'
})

const coresDisponiveis = [
  { nome: 'Azul', valor: '#3b82f6' },
  { nome: 'Verde', valor: '#10b981' },
  { nome: 'Amarelo', valor: '#f59e0b' },
  { nome: 'Vermelho', valor: '#ef4444' },
  { nome: 'Roxo', valor: '#8b5cf6' },
  { nome: 'Rosa', valor: '#ec4899' },
  { nome: 'Indigo', valor: '#6366f1' },
  { nome: 'Laranja', valor: '#f97316' },
]

const iconesDisponiveis = [
  { nome: 'Apresentação', valor: 'presentation', componente: Presentation },
  { nome: 'Prédio', valor: 'building', componente: Building },
  { nome: 'Escritório', valor: 'briefcase', componente: Briefcase },
  { nome: 'Teatro', valor: 'theater', componente: Theater },
  { nome: 'Pin', valor: 'map-pin', componente: MapPin },
]

const iconeMap: Record<string, any> = {
  presentation: Presentation,
  building: Building,
  briefcase: Briefcase,
  theater: Theater,
  'map-pin': MapPin,
}

// Carregar dados
onMounted(async () => {
  await agendaStore.initialize()
})

// Methods
const abrirNovoEspaco = () => {
  espacoEditando.value = null
  form.value = {
    nome: '',
    descricao: '',
    capacidade: 10,
    icone: 'presentation',
    cor: '#3b82f6'
  }
  mostrarModalEspaco.value = true
}

const abrirEdicaoEspaco = (espaco: Espaco) => {
  espacoEditando.value = espaco
  form.value = {
    nome: espaco.nome,
    descricao: espaco.descricao || '',
    capacidade: espaco.capacidade,
    icone: espaco.icone,
    cor: espaco.cor
  }
  mostrarModalEspaco.value = true
}

const salvarEspaco = async () => {
  if (!form.value.nome.trim()) return

  try {
    if (espacoEditando.value) {
      await agendaStore.updateEspaco(espacoEditando.value.id, {
        ...form.value,
        ativo: true
      })
    } else {
      await agendaStore.createEspaco({
        ...form.value,
        ativo: true
      })
    }

    fecharModal()
  } catch (error) {
    console.error(error)
  }
}

const fecharModal = () => {
  mostrarModalEspaco.value = false
  espacoEditando.value = null
  form.value = {
    nome: '',
    descricao: '',
    capacidade: 10,
    icone: 'presentation',
    cor: '#3b82f6'
  }
}

const handleExcluirEspaco = async (espaco: Espaco) => {
  if (confirmandoExclusao.value !== espaco.id) {
    confirmandoExclusao.value = espaco.id
    erroExclusao.value = ''
    setTimeout(() => {
      confirmandoExclusao.value = null
    }, 3000)
    return
  }

  try {
    await agendaStore.deleteEspaco(espaco.id)
    confirmandoExclusao.value = null
    erroExclusao.value = ''
  } catch (error: any) {
    erroExclusao.value = error.message || 'Erro ao excluir espaço'
    confirmandoExclusao.value = null
    setTimeout(() => {
      erroExclusao.value = ''
    }, 5000)
  }
}

const contarEventosNoEspaco = (espacoId: string): number => {
  return agendaStore.getEventosByEspaco(espacoId).length
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <p class="text-sm text-gray-600 dark:text-slate-400">
        Gerencie os espaços físicos disponíveis para reserva
      </p>

      <Button variant="primary" @click="abrirNovoEspaco">
        <Plus class="w-4 h-4" />
        Novo Espaço
      </Button>
    </div>

    <!-- Erro de Exclusão -->
    <div v-if="erroExclusao" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
      <AlertCircle class="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
      <div class="flex-1">
        <p class="text-sm font-medium text-red-900 dark:text-red-300">
          Erro ao excluir espaço
        </p>
        <p class="text-sm text-red-700 dark:text-red-400 mt-1">
          {{ erroExclusao }}
        </p>
      </div>
    </div>

    <!-- Grid de Espaços -->
    <div v-if="agendaStore.espacos.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="espaco in agendaStore.espacos"
        :key="espaco.id"
        class="card group hover:shadow-lg transition-all"
      >
        <!-- Header do Card -->
        <div class="flex items-start justify-between mb-4">
          <div
            class="w-16 h-16 rounded-xl flex items-center justify-center"
            :style="{ backgroundColor: espaco.cor + '20' }"
          >
            <component
              :is="iconeMap[espaco.icone] || MapPin"
              class="w-8 h-8"
              :style="{ color: espaco.cor }"
            />
          </div>

          <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              @click="abrirEdicaoEspaco(espaco)"
              class="p-2 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg text-gray-600 dark:text-slate-400"
              title="Editar espaço"
            >
              <Edit class="w-4 h-4" />
            </button>
            <button
              @click="handleExcluirEspaco(espaco)"
              :class="[
                confirmandoExclusao === espaco.id
                  ? 'bg-red-500 text-white'
                  : 'text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30',
                'p-2 rounded-lg transition-colors'
              ]"
              :title="confirmandoExclusao === espaco.id ? 'Confirmar exclusão' : 'Excluir espaço'"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Conteúdo -->
        <h3 class="text-lg font-semibold text-gray-900 dark:text-slate-100 mb-2">
          {{ espaco.nome }}
        </h3>

        <p v-if="espaco.descricao" class="text-sm text-gray-600 dark:text-slate-400 mb-4 line-clamp-2">
          {{ espaco.descricao }}
        </p>

        <RastreabilidadeMeta
          :rastreabilidade="espaco.rastreabilidade"
          :alvo-auditoria="AUDITORIA_ALVO.espaco(espaco.id)"
          historico-titulo="Histórico do espaço"
          compact
          class="mb-3"
        />

        <!-- Stats -->
        <div class="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-slate-700">
          <div class="flex items-center gap-2">
            <Users class="w-4 h-4 text-gray-400 dark:text-slate-500" />
            <span class="text-sm text-gray-700 dark:text-slate-300">
              <strong>{{ espaco.capacidade }}</strong> pessoas
            </span>
          </div>

          <div class="text-sm text-gray-500 dark:text-slate-400">
            {{ contarEventosNoEspaco(espaco.id) }} evento(s)
          </div>
        </div>

        <!-- Badge de Status -->
        <div class="mt-3">
          <span
            :class="[
              espaco.ativo
                ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
                : 'bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-slate-300',
              'inline-flex items-center px-2 py-1 rounded text-xs font-medium'
            ]"
          >
            {{ espaco.ativo ? 'Ativo' : 'Inativo' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="card text-center py-12">
      <MapPin class="w-16 h-16 text-gray-300 dark:text-slate-600 mx-auto mb-4" />
      <h3 class="text-lg font-semibold text-gray-900 dark:text-slate-100 mb-2">
        Nenhum espaço cadastrado
      </h3>
      <p class="text-sm text-gray-600 dark:text-slate-400 mb-4">
        Cadastre os espaços físicos disponíveis para reserva de eventos
      </p>
      <Button variant="primary" @click="abrirNovoEspaco">
        <Plus class="w-4 h-4" />
        Cadastrar Primeiro Espaço
      </Button>
    </div>

    <!-- Modal de Espaço -->
    <Modal
      :model-value="mostrarModalEspaco"
      @update:model-value="fecharModal"
      :titulo="espacoEditando ? 'Editar Espaço' : 'Novo Espaço'"
      largura="md"
    >
      <form @submit.prevent="salvarEspaco" class="space-y-4">
        <!-- Nome -->
        <div>
          <label class="label">Nome do Espaço *</label>
          <input
            v-model="form.nome"
            type="text"
            class="input"
            placeholder="Ex: Sala de Reuniões 2"
            required
          />
        </div>

        <!-- Descrição -->
        <div>
          <label class="label">Descrição</label>
          <textarea
            v-model="form.descricao"
            rows="2"
            class="input"
            placeholder="Equipamentos, recursos disponíveis..."
          ></textarea>
        </div>

        <!-- Capacidade -->
        <div>
          <label class="label">Capacidade (pessoas) *</label>
          <input
            v-model.number="form.capacidade"
            type="number"
            min="1"
            max="1000"
            class="input"
            required
          />
        </div>

        <!-- Cor -->
        <div>
          <label class="label">Cor de Identificação</label>
          <div class="grid grid-cols-4 gap-2">
            <button
              v-for="cor in coresDisponiveis"
              :key="cor.valor"
              @click="form.cor = cor.valor"
              type="button"
              :class="[
                form.cor === cor.valor
                  ? 'ring-2 ring-offset-2 ring-primary-600 dark:ring-offset-slate-800'
                  : '',
                'w-full h-10 rounded-lg transition-all hover:scale-105'
              ]"
              :style="{ backgroundColor: cor.valor }"
              :title="cor.nome"
            ></button>
          </div>
        </div>

        <!-- Ícone -->
        <div>
          <label class="label">Ícone</label>
          <div class="grid grid-cols-5 gap-2">
            <button
              v-for="icone in iconesDisponiveis"
              :key="icone.valor"
              @click="form.icone = icone.valor"
              type="button"
              :class="[
                form.icone === icone.valor
                  ? 'bg-primary-100 dark:bg-primary-900/30 border-primary-500 dark:border-primary-600'
                  : 'bg-white dark:bg-slate-800 border-gray-300 dark:border-slate-600',
                'h-12 border-2 rounded-lg flex items-center justify-center transition-all hover:scale-105'
              ]"
              :title="icone.nome"
            >
              <component
                :is="icone.componente"
                class="w-5 h-5"
                :class="form.icone === icone.valor ? 'text-primary-600 dark:text-primary-400' : 'text-gray-600 dark:text-slate-400'"
              />
            </button>
          </div>
        </div>

        <!-- Preview -->
        <div class="p-4 bg-gray-50 dark:bg-slate-900 rounded-lg">
          <p class="text-xs text-gray-600 dark:text-slate-400 mb-3">Preview:</p>
          <div class="flex items-center gap-4">
            <div
              class="w-16 h-16 rounded-xl flex items-center justify-center flex-shrink-0"
              :style="{ backgroundColor: form.cor + '20' }"
            >
              <component
                :is="iconeMap[form.icone] || MapPin"
                class="w-8 h-8"
                :style="{ color: form.cor }"
              />
            </div>
            <div class="flex-1">
              <h4 class="font-semibold text-gray-900 dark:text-slate-100">
                {{ form.nome || 'Nome do Espaço' }}
              </h4>
              <p v-if="form.descricao" class="text-sm text-gray-600 dark:text-slate-400 mt-1">
                {{ form.descricao }}
              </p>
              <div class="flex items-center gap-2 mt-2">
                <Users class="w-4 h-4 text-gray-400 dark:text-slate-500" />
                <span class="text-sm text-gray-700 dark:text-slate-300">
                  {{ form.capacidade }} pessoas
                </span>
              </div>
            </div>
          </div>
        </div>
      </form>

      <template #footer>
        <Button variant="secondary" @click="fecharModal">
          Cancelar
        </Button>
        <Button variant="primary" @click="salvarEspaco" :disabled="!form.nome.trim()">
          {{ espacoEditando ? 'Salvar Alterações' : 'Criar Espaço' }}
        </Button>
      </template>
    </Modal>
  </div>
</template>
