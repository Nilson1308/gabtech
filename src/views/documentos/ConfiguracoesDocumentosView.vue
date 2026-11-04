<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useDocumentosStore } from '@/stores/documentos'
import { useTiposDocumentoStore } from '@/stores/tiposDocumento'
import { useAuthStore } from '@/stores/auth'
import { useAlertDialog } from '@/composables/useAlertDialog'
import type { EtiquetaDocumento, PastaDocumento } from '@/types'
import type { TipoDocumentoCustom } from '@/stores/tiposDocumento'
import { 
  Folder,
  Plus,
  Edit,
  Trash2,
  X,
  Save,
  FileType,
  Palette,
  Tag
} from 'lucide-vue-next'

const documentosStore = useDocumentosStore()
const tiposStore = useTiposDocumentoStore()
const authStore = useAuthStore()
const { showSuccess, showError, showConfirm } = useAlertDialog()

const abaSelecionada = ref<'pastas' | 'tipos' | 'etiquetas'>('pastas')
const modoEdicao = ref<'criar' | 'editar' | null>(null)
const itemSelecionado = ref<any>(null)

// Form Pasta
const formPasta = ref({
  nome: '',
  icone: 'folder',
  cor: '#3b82f6'
})

// Form Tipo
const formTipo = ref({
  nome: '',
  descricao: '',
  icone: 'file-text',
  cor: '#3b82f6'
})

const formEtiqueta = ref({
  nome: '',
  cor: '#6b7280',
})

const coresDisponiveis = [
  { nome: 'Azul', valor: '#3b82f6' },
  { nome: 'Verde', valor: '#10b981' },
  { nome: 'Amarelo', valor: '#f59e0b' },
  { nome: 'Roxo', valor: '#8b5cf6' },
  { nome: 'Rosa', valor: '#ec4899' },
  { nome: 'Vermelho', valor: '#ef4444' },
  { nome: 'Índigo', valor: '#6366f1' },
  { nome: 'Ciano', valor: '#06b6d4' },
  { nome: 'Laranja', valor: '#f97316' },
  { nome: 'Lima', valor: '#84cc16' },
  { nome: 'Cinza', valor: '#6b7280' },
]

onMounted(async () => {
  await Promise.all([
    documentosStore.initializeCatalogo(),
    documentosStore.fetchResumo(),
    tiposStore.initialize(),
  ])
})

const pastasOrdenadas = computed(() => {
  return [...documentosStore.pastas].sort((a, b) => 
    a.nome.localeCompare(b.nome)
  )
})

const tiposOrdenados = computed(() => {
  return [...tiposStore.tipos].sort((a, b) => {
    if (a.isSystem && !b.isSystem) return -1
    if (!a.isSystem && b.isSystem) return 1
    return a.nome.localeCompare(b.nome)
  })
})

const etiquetasOrdenadas = computed(() =>
  [...documentosStore.etiquetas].sort((a, b) => a.nome.localeCompare(b.nome)),
)

function contarDocumentosPorPasta(pastaId: string) {
  return documentosStore.contarDocumentosNaPasta(pastaId)
}

// Funções Pasta
function novaPasta() {
  formPasta.value = {
    nome: '',
    icone: 'folder',
    cor: '#3b82f6'
  }
  itemSelecionado.value = null
  modoEdicao.value = 'criar'
  abaSelecionada.value = 'pastas'
}

function editarPasta(pasta: PastaDocumento) {
  formPasta.value = {
    nome: pasta.nome,
    icone: pasta.icone || 'folder',
    cor: pasta.cor || '#3b82f6'
  }
  itemSelecionado.value = pasta
  modoEdicao.value = 'editar'
  abaSelecionada.value = 'pastas'
}

async function salvarPasta() {
  if (!formPasta.value.nome.trim()) {
    showError('Por favor, preencha o nome da pasta')
    return
  }

  try {
    if (modoEdicao.value === 'criar') {
      await documentosStore.createPasta(formPasta.value)
      showSuccess('Pasta criada com sucesso!')
    } else if (modoEdicao.value === 'editar' && itemSelecionado.value) {
      await documentosStore.updatePasta(itemSelecionado.value.id, formPasta.value)
      showSuccess('Pasta atualizada com sucesso!')
    }
    fecharModal()
  } catch (error: any) {
    showError(error.message || 'Erro ao salvar pasta')
  }
}

async function excluirPasta(pasta: PastaDocumento) {
  const qtdDocs = contarDocumentosPorPasta(pasta.id)
  
  if (qtdDocs > 0) {
    showError(`Esta pasta contém ${qtdDocs} documento(s). Mova ou exclua os documentos antes de excluir a pasta.`)
    return
  }

  const confirmed = await showConfirm(`Tem certeza que deseja excluir a pasta "${pasta.nome}"?`)
  if (!confirmed) return

  try {
    await documentosStore.deletePasta(pasta.id)
    showSuccess('Pasta excluída com sucesso!')
  } catch (error: any) {
    showError(error.message || 'Erro ao excluir pasta')
  }
}

// Funções Tipo
function novoTipo() {
  formTipo.value = {
    nome: '',
    descricao: '',
    icone: 'file-text',
    cor: '#3b82f6'
  }
  itemSelecionado.value = null
  modoEdicao.value = 'criar'
  abaSelecionada.value = 'tipos'
}

function editarTipo(tipo: TipoDocumentoCustom) {
  if (tipo.isSystem) {
    showError('Tipos do sistema não podem ser editados')
    return
  }

  formTipo.value = {
    nome: tipo.nome,
    descricao: tipo.descricao || '',
    icone: tipo.icone || 'file-text',
    cor: tipo.cor || '#3b82f6'
  }
  itemSelecionado.value = tipo
  modoEdicao.value = 'editar'
  abaSelecionada.value = 'tipos'
}

async function salvarTipo() {
  if (!formTipo.value.nome.trim()) {
    showError('Por favor, preencha o nome do tipo')
    return
  }

  try {
    if (modoEdicao.value === 'criar') {
      await tiposStore.createTipo({
        nome: formTipo.value.nome,
        slug: '', // será gerado automaticamente na store
        descricao: formTipo.value.descricao,
        icone: formTipo.value.icone,
        cor: formTipo.value.cor
      })
      showSuccess('Tipo de documento criado com sucesso!')
    } else if (modoEdicao.value === 'editar' && itemSelecionado.value) {
      await tiposStore.updateTipo(itemSelecionado.value.id, {
        nome: formTipo.value.nome,
        descricao: formTipo.value.descricao,
        icone: formTipo.value.icone,
        cor: formTipo.value.cor
      })
      showSuccess('Tipo atualizado com sucesso!')
    }
    fecharModal()
  } catch (error: any) {
    showError(error.message || 'Erro ao salvar tipo')
  }
}

async function excluirTipo(tipo: TipoDocumentoCustom) {
  if (tipo.isSystem) {
    showError('Tipos do sistema não podem ser excluídos')
    return
  }

  const confirmed = await showConfirm(`Tem certeza que deseja excluir o tipo "${tipo.nome}"?`)
  if (!confirmed) return

  try {
    await tiposStore.deleteTipo(tipo.id)
    showSuccess('Tipo excluído com sucesso!')
  } catch (error: any) {
    showError(error.message || 'Erro ao excluir tipo')
  }
}

function fecharModal() {
  modoEdicao.value = null
  itemSelecionado.value = null
}

function novaEtiqueta() {
  formEtiqueta.value = { nome: '', cor: '#6b7280' }
  itemSelecionado.value = null
  modoEdicao.value = 'criar'
  abaSelecionada.value = 'etiquetas'
}

function editarEtiqueta(etiqueta: EtiquetaDocumento) {
  formEtiqueta.value = { nome: etiqueta.nome, cor: etiqueta.cor }
  itemSelecionado.value = etiqueta
  modoEdicao.value = 'editar'
  abaSelecionada.value = 'etiquetas'
}

async function salvarEtiqueta() {
  if (!formEtiqueta.value.nome.trim()) {
    showError('Informe o nome da etiqueta')
    return
  }
  try {
    if (modoEdicao.value === 'criar') {
      await documentosStore.createEtiqueta(formEtiqueta.value)
      showSuccess('Etiqueta criada com sucesso!')
    } else if (modoEdicao.value === 'editar' && itemSelecionado.value) {
      await documentosStore.updateEtiqueta(itemSelecionado.value.id, formEtiqueta.value)
      showSuccess('Etiqueta atualizada!')
    }
    fecharModal()
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Erro ao salvar etiqueta'
    showError(message)
  }
}

async function excluirEtiqueta(etiqueta: EtiquetaDocumento) {
  const qtd = documentosStore.contarDocumentosPorEtiqueta(etiqueta.id)
  if (qtd > 0) {
    showError(`Esta etiqueta está em ${qtd} documento(s). Remova dos documentos antes de excluir.`)
    return
  }
  const ok = await showConfirm(`Excluir a etiqueta «${etiqueta.nome}»?`)
  if (!ok) return
  try {
    await documentosStore.deleteEtiqueta(etiqueta.id)
    showSuccess('Etiqueta excluída.')
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Erro ao excluir etiqueta'
    showError(message)
  }
}

function tituloModal() {
  if (abaSelecionada.value === 'pastas') {
    return modoEdicao.value === 'criar' ? 'Nova Pasta' : 'Editar Pasta'
  }
  if (abaSelecionada.value === 'etiquetas') {
    return modoEdicao.value === 'criar' ? 'Nova Etiqueta' : 'Editar Etiqueta'
  }
  return modoEdicao.value === 'criar' ? 'Novo Tipo de Documento' : 'Editar Tipo'
}

function salvarModal() {
  if (abaSelecionada.value === 'pastas') return salvarPasta()
  if (abaSelecionada.value === 'etiquetas') return salvarEtiqueta()
  return salvarTipo()
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <p class="text-gray-600 dark:text-gray-400">
          Gerencie pastas, tipos e etiquetas de documentos
        </p>
      </div>

      <button
        v-if="authStore.hasPermission('criar_docs')"
        @click="abaSelecionada === 'pastas' ? novaPasta() : abaSelecionada === 'etiquetas' ? novaEtiqueta() : novoTipo()"
        class="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors"
      >
        <Plus class="w-5 h-5" />
        {{
          abaSelecionada === 'pastas'
            ? 'Nova Pasta'
            : abaSelecionada === 'etiquetas'
              ? 'Nova Etiqueta'
              : 'Novo Tipo'
        }}
      </button>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="flex gap-4">
        <button
          @click="abaSelecionada = 'pastas'"
          :class="[
            abaSelecionada === 'pastas'
              ? 'border-primary-600 text-primary-600 dark:border-primary-400 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600',
            'flex items-center gap-2 px-4 py-3 border-b-2 font-medium transition-colors'
          ]"
        >
          <Folder class="w-5 h-5" />
          Pastas ({{ pastasOrdenadas.length }})
        </button>

        <button
          @click="abaSelecionada = 'tipos'"
          :class="[
            abaSelecionada === 'tipos'
              ? 'border-primary-600 text-primary-600 dark:border-primary-400 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600',
            'flex items-center gap-2 px-4 py-3 border-b-2 font-medium transition-colors'
          ]"
        >
          <FileType class="w-5 h-5" />
          Tipos de Documento ({{ tiposOrdenados.length }})
        </button>

        <button
          @click="abaSelecionada = 'etiquetas'"
          :class="[
            abaSelecionada === 'etiquetas'
              ? 'border-primary-600 text-primary-600 dark:border-primary-400 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600',
            'flex items-center gap-2 px-4 py-3 border-b-2 font-medium transition-colors'
          ]"
        >
          <Tag class="w-5 h-5" />
          Etiquetas ({{ etiquetasOrdenadas.length }})
        </button>
      </nav>
    </div>

    <!-- Conteúdo Pastas -->
    <div v-if="abaSelecionada === 'pastas'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="pasta in pastasOrdenadas"
        :key="pasta.id"
        class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:shadow-lg transition-shadow"
      >
        <div class="flex items-start justify-between mb-3">
          <div class="flex items-center gap-3 flex-1 min-w-0">
            <div
              class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
              :style="{ backgroundColor: pasta.cor + '20', color: pasta.cor }"
            >
              <Folder class="w-6 h-6" />
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 truncate">
                {{ pasta.nome }}
              </h3>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                {{ contarDocumentosPorPasta(pasta.id) }} documento(s)
              </p>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button
            v-if="authStore.hasPermission('editar_docs')"
            @click="editarPasta(pasta)"
            class="flex-1 flex items-center justify-center gap-1 px-3 py-1.5 text-sm bg-blue-100 hover:bg-blue-200 dark:bg-blue-900/30 dark:hover:bg-blue-900/50 text-blue-700 dark:text-blue-400 rounded transition-colors"
          >
            <Edit class="w-4 h-4" />
            Editar
          </button>

          <button
            v-if="authStore.hasPermission('excluir_docs')"
            @click="excluirPasta(pasta)"
            class="p-1.5 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
            title="Excluir"
          >
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
      </div>

      <div v-if="pastasOrdenadas.length === 0" class="col-span-full text-center py-12">
        <Folder class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
        <p class="text-gray-500 dark:text-gray-400">Nenhuma pasta cadastrada</p>
      </div>
    </div>

    <!-- Conteúdo Tipos -->
    <div v-if="abaSelecionada === 'tipos'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="tipo in tiposOrdenados"
        :key="tipo.id"
        class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:shadow-lg transition-shadow"
      >
        <div class="flex items-start justify-between mb-3">
          <div class="flex items-center gap-3 flex-1 min-w-0">
            <div
              class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
              :style="{ backgroundColor: tipo.cor + '20', color: tipo.cor }"
            >
              <FileType class="w-6 h-6" />
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 truncate">
                {{ tipo.nome }}
              </h3>
              <span
                v-if="tipo.isSystem"
                class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 mt-1"
              >
                Sistema
              </span>
            </div>
          </div>
        </div>

        <p v-if="tipo.descricao" class="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
          {{ tipo.descricao }}
        </p>

        <div class="flex items-center gap-2">
          <button
            v-if="!tipo.isSystem && authStore.hasPermission('editar_docs')"
            @click="editarTipo(tipo)"
            class="flex-1 flex items-center justify-center gap-1 px-3 py-1.5 text-sm bg-blue-100 hover:bg-blue-200 dark:bg-blue-900/30 dark:hover:bg-blue-900/50 text-blue-700 dark:text-blue-400 rounded transition-colors"
          >
            <Edit class="w-4 h-4" />
            Editar
          </button>

          <button
            v-if="!tipo.isSystem && authStore.hasPermission('excluir_docs')"
            @click="excluirTipo(tipo)"
            class="p-1.5 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
            title="Excluir"
          >
            <Trash2 class="w-4 h-4" />
          </button>

          <span
            v-if="tipo.isSystem"
            class="flex-1 text-center text-sm text-gray-500 dark:text-gray-400 italic"
          >
            Protegido
          </span>
        </div>
      </div>

      <div v-if="tiposOrdenados.length === 0" class="col-span-full text-center py-12">
        <FileType class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
        <p class="text-gray-500 dark:text-gray-400">Nenhum tipo cadastrado</p>
      </div>
    </div>

    <!-- Conteúdo Etiquetas -->
    <div v-else-if="abaSelecionada === 'etiquetas'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="etiqueta in etiquetasOrdenadas"
        :key="etiqueta.id"
        class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:shadow-lg transition-shadow"
      >
        <div class="flex items-start gap-3 mb-3">
          <div
            class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
            :style="{ backgroundColor: etiqueta.cor + '25', color: etiqueta.cor }"
          >
            <Tag class="w-5 h-5" />
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-gray-900 dark:text-gray-100 truncate">{{ etiqueta.nome }}</h3>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              {{ documentosStore.contarDocumentosPorEtiqueta(etiqueta.id) }} documento(s)
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button
            v-if="authStore.hasPermission('editar_docs')"
            @click="editarEtiqueta(etiqueta)"
            class="flex-1 flex items-center justify-center gap-1 px-3 py-1.5 text-sm bg-blue-100 hover:bg-blue-200 dark:bg-blue-900/30 dark:hover:bg-blue-900/50 text-blue-700 dark:text-blue-400 rounded transition-colors"
          >
            <Edit class="w-4 h-4" />
            Editar
          </button>
          <button
            v-if="authStore.hasPermission('editar_docs')"
            @click="excluirEtiqueta(etiqueta)"
            class="p-1.5 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
            title="Excluir"
          >
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
      </div>
      <div v-if="etiquetasOrdenadas.length === 0" class="col-span-full text-center py-12">
        <Tag class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
        <p class="text-gray-500 dark:text-gray-400">Nenhuma etiqueta cadastrada</p>
      </div>
    </div>

    <!-- Modal de Criação/Edição -->
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="modoEdicao"
        class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
        @click.self="fecharModal"
      >
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-lg w-full">
          <!-- Header -->
          <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {{ tituloModal() }}
            </h3>
            <button
              @click="fecharModal"
              class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded transition-colors"
            >
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- Conteúdo -->
          <div class="p-6 space-y-4">
            <!-- Form Pasta -->
            <div v-if="abaSelecionada === 'pastas'" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Nome da Pasta *
                </label>
                <input
                  v-model="formPasta.nome"
                  type="text"
                  placeholder="Ex: Correspondências 2026"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
                  <Palette class="w-4 h-4" />
                  Cor
                </label>
                <div class="grid grid-cols-6 gap-2">
                  <button
                    v-for="cor in coresDisponiveis"
                    :key="cor.valor"
                    @click="formPasta.cor = cor.valor"
                    :class="[
                      formPasta.cor === cor.valor && 'ring-2 ring-offset-2 ring-gray-400 dark:ring-gray-500',
                      'w-full h-10 rounded-lg transition-all hover:scale-110'
                    ]"
                    :style="{ backgroundColor: cor.valor }"
                    :title="cor.nome"
                  />
                </div>
              </div>
            </div>

            <!-- Form Etiqueta -->
            <div v-else-if="abaSelecionada === 'etiquetas'" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Nome da Etiqueta *
                </label>
                <input
                  v-model="formEtiqueta.nome"
                  type="text"
                  placeholder="Ex: Urgente, Educação, Administrativo"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
                  <Palette class="w-4 h-4" />
                  Cor
                </label>
                <div class="grid grid-cols-6 gap-2">
                  <button
                    v-for="cor in coresDisponiveis"
                    :key="cor.valor"
                    type="button"
                    @click="formEtiqueta.cor = cor.valor"
                    :class="[
                      formEtiqueta.cor === cor.valor && 'ring-2 ring-offset-2 ring-gray-400 dark:ring-gray-500',
                      'w-full h-10 rounded-lg transition-all hover:scale-110'
                    ]"
                    :style="{ backgroundColor: cor.valor }"
                    :title="cor.nome"
                  />
                </div>
              </div>
            </div>

            <!-- Form Tipo -->
            <div v-else class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Nome do Tipo *
                </label>
                <input
                  v-model="formTipo.nome"
                  type="text"
                  placeholder="Ex: Moção de Apoio"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Descrição
                </label>
                <textarea
                  v-model="formTipo.descricao"
                  rows="2"
                  placeholder="Breve descrição do tipo de documento..."
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400 resize-none"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
                  <Palette class="w-4 h-4" />
                  Cor
                </label>
                <div class="grid grid-cols-6 gap-2">
                  <button
                    v-for="cor in coresDisponiveis"
                    :key="cor.valor"
                    @click="formTipo.cor = cor.valor"
                    :class="[
                      formTipo.cor === cor.valor && 'ring-2 ring-offset-2 ring-gray-400 dark:ring-gray-500',
                      'w-full h-10 rounded-lg transition-all hover:scale-110'
                    ]"
                    :style="{ backgroundColor: cor.valor }"
                    :title="cor.nome"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="flex items-center justify-end gap-3 p-4 border-t border-gray-200 dark:border-gray-700">
            <button
              @click="fecharModal"
              class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              Cancelar
            </button>
            <button
              @click="salvarModal()"
              :disabled="documentosStore.loading || tiposStore.loading"
              class="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              <Save class="w-4 h-4" />
              {{ modoEdicao === 'criar' ? 'Criar' : 'Salvar' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
