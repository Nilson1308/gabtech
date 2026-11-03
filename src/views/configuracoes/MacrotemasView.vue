<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAtendimentosStore } from '@/stores/atendimentos'
import type { Macrotema } from '@/types'
import Button from '@/components/common/Button.vue'
import RastreabilidadeMeta from '@/components/common/RastreabilidadeMeta.vue'
import { AUDITORIA_ALVO } from '@/services/auditoria'
import Modal from '@/components/common/Modal.vue'
import { 
  Plus, 
  Edit, 
  Trash2, 
  AlertCircle, 
  FolderTree,
  HeartPulse,
  GraduationCap,
  Wrench,
  Bus,
  Users,
  Shield
} from 'lucide-vue-next'

const atendimentosStore = useAtendimentosStore()

// Estado
const mostrarModal = ref(false)
const macrotemaEditando = ref<Macrotema | null>(null)
const confirmandoExclusao = ref<string | null>(null)
const mostrarAvisoUso = ref(false)
const quantidadeUso = ref(0)

// Form
const form = ref({
  nome: '',
  cor: '#3b82f6',
  icone: 'folder-tree'
})

const cores = [
  { nome: 'Azul', valor: '#3b82f6' },
  { nome: 'Verde', valor: '#10b981' },
  { nome: 'Amarelo', valor: '#f59e0b' },
  { nome: 'Vermelho', valor: '#ef4444' },
  { nome: 'Roxo', valor: '#8b5cf6' },
  { nome: 'Rosa', valor: '#ec4899' },
  { nome: 'Cinza', valor: '#6b7280' },
  { nome: 'Laranja', valor: '#f97316' },
  { nome: 'Teal', valor: '#14b8a6' },
  { nome: 'Vermelho Escuro', valor: '#dc2626' },
]

const iconesDisponiveis = [
  { nome: 'Pasta', valor: 'folder-tree', componente: FolderTree },
  { nome: 'Saúde', valor: 'heart-pulse', componente: HeartPulse },
  { nome: 'Educação', valor: 'graduation-cap', componente: GraduationCap },
  { nome: 'Zeladoria', valor: 'wrench', componente: Wrench },
  { nome: 'Transporte', valor: 'bus', componente: Bus },
  { nome: 'Pessoas', valor: 'users', componente: Users },
  { nome: 'Segurança', valor: 'shield', componente: Shield },
]

const iconeMap: Record<string, any> = {
  'folder-tree': FolderTree,
  'heart-pulse': HeartPulse,
  'graduation-cap': GraduationCap,
  'wrench': Wrench,
  'bus': Bus,
  'users': Users,
  'shield': Shield,
}

const macrotemas = computed(() => atendimentosStore.macrotemasDisponiveis)

onMounted(async () => {
  await Promise.all([
    atendimentosStore.fetchMacrotemas(),
    atendimentosStore.fetchAtendimentos(),
  ])
})

const abrirNovo = () => {
  macrotemaEditando.value = null
  form.value = {
    nome: '',
    cor: '#3b82f6',
    icone: 'folder-tree'
  }
  mostrarModal.value = true
}

const abrirEdicao = (macrotema: Macrotema) => {
  macrotemaEditando.value = macrotema
  form.value = {
    nome: macrotema.nome,
    cor: macrotema.cor,
    icone: macrotema.icone || 'folder-tree'
  }
  mostrarModal.value = true
}

const salvar = async () => {
  if (!form.value.nome.trim()) {
    return
  }

  if (macrotemaEditando.value) {
    await atendimentosStore.updateMacrotema(macrotemaEditando.value.id, {
      nome: form.value.nome,
      cor: form.value.cor,
      icone: form.value.icone,
    })
  } else {
    await atendimentosStore.createMacrotema({
      nome: form.value.nome,
      cor: form.value.cor,
      icone: form.value.icone,
    })
  }

  fecharModal()
}

const fecharModal = () => {
  mostrarModal.value = false
  macrotemaEditando.value = null
  form.value = {
    nome: '',
    cor: '#3b82f6',
    icone: 'folder-tree'
  }
}

const handleExcluir = (macrotema: Macrotema) => {
  // Verificar se o macrotema está em uso
  const emUso = atendimentosStore.atendimentos.filter(a => a.macrotema.id === macrotema.id).length
  
  if (emUso > 0) {
    quantidadeUso.value = emUso
    mostrarAvisoUso.value = true
    return
  }

  if (confirmandoExclusao.value !== macrotema.id) {
    confirmandoExclusao.value = macrotema.id
    setTimeout(() => {
      confirmandoExclusao.value = null
    }, 3000)
    return
  }

  atendimentosStore.deleteMacrotema(macrotema.id)
  confirmandoExclusao.value = null
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
          {{ macrotemas.length }} {{ macrotemas.length === 1 ? 'macrotema cadastrado' : 'macrotemas cadastrados' }}
        </p>
      </div>

      <Button variant="primary" @click="abrirNovo">
        <Plus class="w-4 h-4" />
        Novo Macrotema
      </Button>
    </div>

    <!-- Lista de Macrotemas -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="macrotema in macrotemas"
        :key="macrotema.id"
        class="card group hover:shadow-lg transition-all"
      >
        <div class="flex items-center gap-3 mb-3">
          <div
            class="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0"
            :style="{
              backgroundColor: macrotema.cor + '20',
              color: macrotema.cor
            }"
          >
            <component
              :is="iconeMap[macrotema.icone || 'folder-tree']"
              class="w-6 h-6"
            />
          </div>

          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-gray-900 dark:text-slate-100 truncate">
              {{ macrotema.nome }}
            </h3>
            <p class="text-xs text-gray-500 dark:text-slate-400">
              {{ atendimentosStore.atendimentos.filter(a => a.macrotema.id === macrotema.id).length }} atendimento(s)
            </p>
            <RastreabilidadeMeta
              :rastreabilidade="macrotema.rastreabilidade"
              :alvo-auditoria="AUDITORIA_ALVO.macrotema(macrotema.id)"
              historico-titulo="Histórico do macrotema"
              compact
              class="mt-1"
            />
          </div>

          <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              @click="abrirEdicao(macrotema)"
              class="p-1.5 hover:bg-gray-100 dark:hover:bg-slate-700 rounded text-gray-600 dark:text-slate-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
              title="Editar"
            >
              <Edit class="w-4 h-4" />
            </button>
            <button
              @click="handleExcluir(macrotema)"
              :class="[
                confirmandoExclusao === macrotema.id
                  ? 'bg-red-500 text-white'
                  : 'hover:bg-red-50 dark:hover:bg-red-900/30 text-red-600 dark:text-red-400',
                'p-1.5 rounded transition-colors'
              ]"
              :title="confirmandoExclusao === macrotema.id ? 'Confirmar exclusão' : 'Excluir'"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="macrotemas.length === 0" class="card text-center py-12">
      <FolderTree class="w-16 h-16 text-gray-300 dark:text-slate-600 mx-auto mb-4" />
      <p class="text-gray-500 dark:text-slate-400">Nenhum macrotema cadastrado</p>
    </div>

    <!-- Modal de Macrotema -->
    <Modal
      :model-value="mostrarModal"
      @update:model-value="fecharModal"
      :titulo="macrotemaEditando ? 'Editar Macrotema' : 'Novo Macrotema'"
      largura="md"
    >
      <form @submit.prevent="salvar" class="space-y-4">
        <div>
          <label class="label">Nome do Macrotema *</label>
          <input
            v-model="form.nome"
            type="text"
            class="input"
            placeholder="Ex: Saúde, Educação, Infraestrutura"
            required
          />
        </div>

        <div>
          <label class="label">Ícone</label>
          <div class="grid grid-cols-7 gap-2">
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

        <div>
          <label class="label">Cor</label>
          <div class="grid grid-cols-5 gap-2">
            <button
              v-for="cor in cores"
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

          <div class="mt-4 p-3 bg-gray-50 dark:bg-slate-900 rounded-lg">
            <p class="text-xs text-gray-600 dark:text-slate-400 mb-2">Preview:</p>
            <div class="flex items-center gap-3">
              <div
                class="w-12 h-12 rounded-lg flex items-center justify-center"
                :style="{ backgroundColor: form.cor + '20', color: form.cor }"
              >
                <component
                  :is="iconeMap[form.icone]"
                  class="w-6 h-6"
                />
              </div>
              <span class="font-semibold text-gray-900 dark:text-slate-100">
                {{ form.nome || 'Nome do Macrotema' }}
              </span>
            </div>
          </div>
        </div>
      </form>

      <template #footer>
        <Button variant="secondary" @click="fecharModal">
          Cancelar
        </Button>
        <Button variant="primary" @click="salvar" :disabled="!form.nome.trim()">
          {{ macrotemaEditando ? 'Salvar Alterações' : 'Criar Macrotema' }}
        </Button>
      </template>
    </Modal>

    <!-- Modal de Aviso de Uso -->
    <Modal
      :model-value="mostrarAvisoUso"
      @update:model-value="mostrarAvisoUso = false"
      titulo="Macrotema em Uso"
      largura="md"
    >
      <div class="flex gap-4">
        <div class="flex-shrink-0">
          <div class="w-12 h-12 bg-yellow-100 dark:bg-yellow-900/30 rounded-full flex items-center justify-center">
            <AlertCircle class="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
          </div>
        </div>
        <div class="flex-1">
          <p class="text-gray-900 dark:text-slate-100 font-medium mb-2">
            Este macrotema está em uso
          </p>
          <p class="text-sm text-gray-600 dark:text-slate-400">
            Este macrotema está vinculado a <strong>{{ quantidadeUso }}</strong> {{ quantidadeUso === 1 ? 'atendimento' : 'atendimentos' }}. 
            Você deve reatribuir os atendimentos antes de excluí-lo.
          </p>
        </div>
      </div>

      <template #footer>
        <Button variant="primary" @click="mostrarAvisoUso = false">
          Entendi
        </Button>
      </template>
    </Modal>
  </div>
</template>
