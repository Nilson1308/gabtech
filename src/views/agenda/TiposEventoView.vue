<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAgendaStore } from '@/stores/agenda'
import type { TipoEvento } from '@/stores/agenda'
import Button from '@/components/common/Button.vue'
import Modal from '@/components/common/Modal.vue'
import RastreabilidadeMeta from '@/components/common/RastreabilidadeMeta.vue'
import { AUDITORIA_ALVO } from '@/services/auditoria'
import { 
  Plus, 
  Edit, 
  Trash2, 
  Tag,
  AlertCircle
} from 'lucide-vue-next'

const agendaStore = useAgendaStore()

// Estado
const mostrarModalTipo = ref(false)
const tipoEditando = ref<TipoEvento | null>(null)
const confirmandoExclusao = ref<string | null>(null)
const erroExclusao = ref('')

// Form
const form = ref({
  nome: '',
  descricao: '',
  cor: '#3b82f6'
})

const coresDisponiveis = [
  { nome: 'Verde', valor: '#10b981' },
  { nome: 'Azul', valor: '#3b82f6' },
  { nome: 'Amarelo', valor: '#f59e0b' },
  { nome: 'Vermelho', valor: '#ef4444' },
  { nome: 'Roxo', valor: '#8b5cf6' },
  { nome: 'Rosa', valor: '#ec4899' },
  { nome: 'Indigo', valor: '#6366f1' },
  { nome: 'Laranja', valor: '#f97316' },
  { nome: 'Teal', valor: '#14b8a6' },
  { nome: 'Ciano', valor: '#06b6d4' },
]

// Carregar dados
onMounted(async () => {
  await agendaStore.initialize()
})

// Methods
const abrirNovoTipo = () => {
  tipoEditando.value = null
  form.value = {
    nome: '',
    descricao: '',
    cor: '#3b82f6'
  }
  mostrarModalTipo.value = true
}

const abrirEdicaoTipo = (tipo: TipoEvento) => {
  tipoEditando.value = tipo
  form.value = {
    nome: tipo.nome,
    descricao: tipo.descricao || '',
    cor: tipo.cor
  }
  mostrarModalTipo.value = true
}

const salvarTipo = async () => {
  if (!form.value.nome.trim()) return

  try {
    if (tipoEditando.value) {
      await agendaStore.updateTipoEvento(tipoEditando.value.id, {
        ...form.value,
        ativo: true
      })
    } else {
      await agendaStore.createTipoEvento({
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
  mostrarModalTipo.value = false
  tipoEditando.value = null
  form.value = {
    nome: '',
    descricao: '',
    cor: '#3b82f6'
  }
}

const handleExcluirTipo = async (tipo: TipoEvento) => {
  if (confirmandoExclusao.value !== tipo.id) {
    confirmandoExclusao.value = tipo.id
    erroExclusao.value = ''
    setTimeout(() => {
      confirmandoExclusao.value = null
    }, 3000)
    return
  }

  try {
    await agendaStore.deleteTipoEvento(tipo.id)
    confirmandoExclusao.value = null
    erroExclusao.value = ''
  } catch (error: any) {
    erroExclusao.value = error.message || 'Erro ao excluir tipo de evento'
    confirmandoExclusao.value = null
    setTimeout(() => {
      erroExclusao.value = ''
    }, 5000)
  }
}

const contarEventosDoTipo = (tipoId: string): number => {
  return agendaStore.eventos.filter(e => e.tipoId === tipoId && e.status === 'agendado').length
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <p class="text-sm text-gray-600 dark:text-slate-400">
        Gerencie as categorias de eventos da agenda oficial
      </p>

      <Button variant="primary" @click="abrirNovoTipo">
        <Plus class="w-4 h-4" />
        Novo Tipo
      </Button>
    </div>

    <!-- Erro de Exclusão -->
    <div v-if="erroExclusao" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
      <AlertCircle class="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
      <div class="flex-1">
        <p class="text-sm font-medium text-red-900 dark:text-red-300">
          Erro ao excluir tipo de evento
        </p>
        <p class="text-sm text-red-700 dark:text-red-400 mt-1">
          {{ erroExclusao }}
        </p>
      </div>
    </div>

    <!-- Grid de Tipos -->
    <div v-if="agendaStore.tiposEvento.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <div
        v-for="tipo in agendaStore.tiposEvento"
        :key="tipo.id"
        class="card group hover:shadow-lg transition-all relative overflow-hidden"
      >
        <!-- Barra de Cor no Topo -->
        <div 
          class="absolute top-0 left-0 right-0 h-1"
          :style="{ backgroundColor: tipo.cor }"
        ></div>

        <!-- Header do Card -->
        <div class="flex items-start justify-between mt-2">
          <div
            class="w-12 h-12 rounded-lg flex items-center justify-center"
            :style="{ backgroundColor: tipo.cor + '20' }"
          >
            <Tag
              class="w-6 h-6"
              :style="{ color: tipo.cor }"
            />
          </div>

          <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              @click="abrirEdicaoTipo(tipo)"
              class="p-2 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg text-gray-600 dark:text-slate-400"
              title="Editar tipo"
            >
              <Edit class="w-4 h-4" />
            </button>
            <button
              @click="handleExcluirTipo(tipo)"
              :class="[
                confirmandoExclusao === tipo.id
                  ? 'bg-red-500 text-white'
                  : 'text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30',
                'p-2 rounded-lg transition-colors'
              ]"
              :title="confirmandoExclusao === tipo.id ? 'Confirmar exclusão' : 'Excluir tipo'"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Conteúdo -->
        <h3 class="text-lg font-semibold text-gray-900 dark:text-slate-100 mt-3">
          {{ tipo.nome }}
        </h3>

        <p v-if="tipo.descricao" class="text-sm text-gray-600 dark:text-slate-400 mt-1 line-clamp-2">
          {{ tipo.descricao }}
        </p>

        <RastreabilidadeMeta
          :rastreabilidade="tipo.rastreabilidade"
          :alvo-auditoria="AUDITORIA_ALVO.tipoEvento(tipo.id)"
          historico-titulo="Histórico do tipo"
          compact
          class="mt-2"
        />

        <!-- Stats -->
        <div class="flex items-center justify-between pt-4 mt-4 border-t border-gray-200 dark:border-slate-700">
          <div class="text-sm text-gray-500 dark:text-slate-400">
            {{ contarEventosDoTipo(tipo.id) }} evento(s)
          </div>

          <span
            :class="[
              tipo.ativo
                ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
                : 'bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-slate-300',
              'inline-flex items-center px-2 py-1 rounded text-xs font-medium'
            ]"
          >
            {{ tipo.ativo ? 'Ativo' : 'Inativo' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="card text-center py-12">
      <Tag class="w-16 h-16 text-gray-300 dark:text-slate-600 mx-auto mb-4" />
      <h3 class="text-lg font-semibold text-gray-900 dark:text-slate-100 mb-2">
        Nenhum tipo de evento cadastrado
      </h3>
      <p class="text-sm text-gray-600 dark:text-slate-400 mb-4">
        Crie categorias para organizar os eventos da agenda
      </p>
      <Button variant="primary" @click="abrirNovoTipo">
        <Plus class="w-4 h-4" />
        Cadastrar Primeiro Tipo
      </Button>
    </div>

    <!-- Modal de Tipo -->
    <Modal
      :model-value="mostrarModalTipo"
      @update:model-value="fecharModal"
      :titulo="tipoEditando ? 'Editar Tipo de Evento' : 'Novo Tipo de Evento'"
      largura="md"
    >
      <form @submit.prevent="salvarTipo" class="space-y-4">
        <!-- Nome -->
        <div>
          <label class="label">Nome do Tipo *</label>
          <input
            v-model="form.nome"
            type="text"
            class="input"
            placeholder="Ex: Sessão Plenária, Audiência Pública"
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
            placeholder="Breve descrição do tipo de evento..."
          ></textarea>
        </div>

        <!-- Cor -->
        <div>
          <label class="label">Cor de Identificação</label>
          <div class="grid grid-cols-5 gap-2">
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

        <!-- Preview -->
        <div class="p-4 bg-gray-50 dark:bg-slate-900 rounded-lg">
          <p class="text-xs text-gray-600 dark:text-slate-400 mb-3">Preview:</p>
          <div class="relative overflow-hidden rounded-lg border-2 border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-4">
            <div 
              class="absolute top-0 left-0 right-0 h-1"
              :style="{ backgroundColor: form.cor }"
            ></div>
            <div class="flex items-start gap-3 mt-1">
              <div
                class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                :style="{ backgroundColor: form.cor + '20' }"
              >
                <Tag
                  class="w-5 h-5"
                  :style="{ color: form.cor }"
                />
              </div>
              <div class="flex-1">
                <h4 class="font-semibold text-gray-900 dark:text-slate-100">
                  {{ form.nome || 'Nome do Tipo' }}
                </h4>
                <p v-if="form.descricao" class="text-sm text-gray-600 dark:text-slate-400 mt-1">
                  {{ form.descricao }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </form>

      <template #footer>
        <Button variant="secondary" @click="fecharModal">
          Cancelar
        </Button>
        <Button variant="primary" @click="salvarTipo" :disabled="!form.nome.trim()">
          {{ tipoEditando ? 'Salvar Alterações' : 'Criar Tipo' }}
        </Button>
      </template>
    </Modal>
  </div>
</template>
