<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDocumentosStore } from '@/stores/documentos'
import { useAuthStore } from '@/stores/auth'
import { useAlertDialog } from '@/composables/useAlertDialog'
import TipoDocumentoSelector from '@/components/documentos/TipoDocumentoSelector.vue'
import RastreabilidadeMeta from '@/components/common/RastreabilidadeMeta.vue'
import { AUDITORIA_ALVO } from '@/services/auditoria'
import { 
  FileText, 
  FilePlus, 
  Folder, 
  FolderOpen,
  FolderInput,
  Search, 
  MoreVertical,
  FileEdit,
  Eye,
  Trash2,
  ChevronRight,
  Home,
  FileCheck,
  FileWarning,
  FileClock,
  Scale,
  Mail,
  ClipboardList,
  Settings,
  X,
  Check,
  Tag
} from 'lucide-vue-next'
import type { StatusDocumento, TipoDocumento } from '@/types'

const router = useRouter()
const documentosStore = useDocumentosStore()
const authStore = useAuthStore()
const { showConfirm, showInfo } = useAlertDialog()

const busca = ref('')
const menuAbertoId = ref<string | null>(null)
const dataInicio = ref('')
const dataFim = ref('')
const mostrarSeletorTipo = ref(false)
const mostrarModalMoverPasta = ref(false)
const documentoParaMover = ref<string | null>(null)
const pastaDestino = ref<string | undefined>(undefined)

onMounted(() => {
  documentosStore.initialize()
})

// Computed
const documentosExibidos = computed(() => {
  let docs = documentosStore.documentosFiltrados

  // Filtro especial "Sem Pasta"
  if (documentosStore.pastaAtiva === 'sem-pasta') {
    docs = documentosStore.documentos.filter(d => !d.pastaId)
  }

  // Filtrar por busca
  if (busca.value.trim()) {
    const query = busca.value.toLowerCase()
    docs = docs.filter(d =>
      d.titulo.toLowerCase().includes(query) ||
      d.autor.nome.toLowerCase().includes(query) ||
      d.etiquetas.some(e => e.nome.toLowerCase().includes(query)),
    )
  }

  // Filtrar por período
  if (dataInicio.value) {
    docs = docs.filter(d => new Date(d.updatedAt) >= new Date(dataInicio.value))
  }
  if (dataFim.value) {
    docs = docs.filter(d => new Date(d.updatedAt) <= new Date(dataFim.value + 'T23:59:59'))
  }

  return docs
})

const breadcrumbs = computed(() => {
  const items: Array<{ nome: string; id: string | null }> = [{ nome: 'Documentos', id: null }]
  
  if (documentosStore.pastaAtiva === 'sem-pasta') {
    items.push({ nome: 'Sem Pasta', id: 'sem-pasta' })
  } else if (documentosStore.pastaAtiva) {
    const pasta = documentosStore.pastas.find(p => p.id === documentosStore.pastaAtiva)
    if (pasta) {
      items.push({ nome: pasta.nome, id: pasta.id })
    }
  } else if (documentosStore.etiquetaAtiva) {
    const etiqueta = documentosStore.etiquetas.find(e => e.id === documentosStore.etiquetaAtiva)
    if (etiqueta) {
      items.push({ nome: `Etiqueta: ${etiqueta.nome}`, id: etiqueta.id })
    }
  } else if (documentosStore.filtroStatus) {
    const statusLabels = {
      rascunho: 'Rascunhos',
      aguardando_assinatura: 'Pendentes de Assinatura',
      finalizado: 'Finalizados'
    }
    items.push({ nome: statusLabels[documentosStore.filtroStatus], id: null })
  }
  
  return items
})

// Métodos
function contarDocumentosNaPasta(pastaId: string): number {
  return documentosStore.documentos.filter(d => d.pastaId === pastaId).length
}

function selecionarPasta(pastaId: string | null) {
  documentosStore.setPastaAtiva(pastaId)
  documentosStore.setFiltroStatus(null)
  documentosStore.setEtiquetaAtiva(null)
}

function selecionarEtiqueta(etiquetaId: string | null) {
  documentosStore.setEtiquetaAtiva(etiquetaId)
  documentosStore.setPastaAtiva(null)
  documentosStore.setFiltroStatus(null)
}

function selecionarStatus(status: StatusDocumento | null) {
  documentosStore.setFiltroStatus(status)
  documentosStore.setPastaAtiva(null)
  documentosStore.setEtiquetaAtiva(null)
}

function abrirModalMoverPasta(documentoId: string) {
  documentoParaMover.value = documentoId
  const doc = documentosStore.getDocumentoById(documentoId)
  pastaDestino.value = doc?.pastaId
  mostrarModalMoverPasta.value = true
  menuAbertoId.value = null
}

async function confirmarMoverPasta() {
  if (!documentoParaMover.value) return
  
  try {
    await documentosStore.moverParaPasta(documentoParaMover.value, pastaDestino.value || null)
    mostrarModalMoverPasta.value = false
    documentoParaMover.value = null
    pastaDestino.value = undefined
  } catch (error) {
    console.error('Erro ao mover documento:', error)
  }
}

function cancelarMoverPasta() {
  mostrarModalMoverPasta.value = false
  documentoParaMover.value = null
  pastaDestino.value = undefined
}

function novoDocumento() {
  mostrarSeletorTipo.value = true
}

function criarDocumentoComTipo(tipo: TipoDocumento) {
  mostrarSeletorTipo.value = false
  router.push(`/documentos/editor/novo?tipo=${tipo}`)
}

function editarDocumento(id: string) {
  menuAbertoId.value = null
  router.push(`/documentos/editor/${id}`)
}

async function excluirDocumento(id: string) {
  const confirmed = await showConfirm('Tem certeza que deseja excluir este documento?')
  if (confirmed) {
    await documentosStore.deleteDocumento(id)
    menuAbertoId.value = null
  }
}

function visualizarPDF(id: string) {
  // Mock - em produção, geraria PDF para o documento com ID: ${id}
  showInfo(`Visualização de PDF será implementada na integração com backend (Doc ID: ${id})`)
  menuAbertoId.value = null
}

function toggleMenu(id: string) {
  menuAbertoId.value = menuAbertoId.value === id ? null : id
}

function getIconeTipo(tipo: TipoDocumento) {
  const icones: Record<TipoDocumento, any> = {
    oficio: FileText,
    memorando: Mail,
    requerimento: ClipboardList,
    projeto_lei: Scale,
    ata: FileText,
    declaracao: FileText,
    parecer: FileText,
    relatorio: FileText,
    mocao: FileText,
    indicacao: FileText,
    generico: FileText
  }
  return icones[tipo] || FileText
}

function getStatusBadge(status: StatusDocumento) {
  const badges = {
    rascunho: {
      label: 'Rascunho',
      classes: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
    },
    aguardando_assinatura: {
      label: 'Aguardando Assinatura',
      classes: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
    },
    finalizado: {
      label: 'Finalizado',
      classes: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
    }
  }
  return badges[status]
}

function formatarData(data: string) {
  return new Date(data).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<template>
  <div class="flex gap-4 h-[calc(100vh-8rem)]">
    <!-- Sidebar Esquerda - Navegação -->
    <aside class="w-64 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 overflow-y-auto flex-shrink-0">
      <!-- Todos os Documentos -->
      <button
        @click="selecionarPasta(null); documentosStore.setFiltroStatus(null); documentosStore.setEtiquetaAtiva(null)"
        :class="[
          !documentosStore.pastaAtiva && !documentosStore.filtroStatus && !documentosStore.etiquetaAtiva
            ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400 font-medium'
            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700',
          'w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-sm'
        ]"
      >
        <Home class="w-4 h-4 flex-shrink-0" />
        <span>Todos os Documentos</span>
        <span class="ml-auto text-xs">{{ documentosStore.documentos.length }}</span>
      </button>

      <!-- Divider -->
      <div class="my-4 border-t border-gray-200 dark:border-gray-700"></div>

      <!-- Status -->
      <div class="mb-4">
        <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 px-3">
          Por Status
        </h3>
        <div class="space-y-1">
          <button
            @click="selecionarStatus('rascunho')"
            :class="[
              documentosStore.filtroStatus === 'rascunho'
                ? 'bg-gray-100 text-gray-900 dark:bg-gray-700 dark:text-gray-100 font-medium'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700',
              'w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-sm'
            ]"
          >
            <FileClock class="w-4 h-4 flex-shrink-0 text-gray-500 dark:text-gray-400" />
            <span>Rascunhos</span>
            <span class="ml-auto text-xs">{{ documentosStore.documentosPorStatus.rascunho }}</span>
          </button>

          <button
            @click="selecionarStatus('aguardando_assinatura')"
            :class="[
              documentosStore.filtroStatus === 'aguardando_assinatura'
                ? 'bg-amber-100 text-amber-900 dark:bg-amber-900/30 dark:text-amber-400 font-medium'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700',
              'w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-sm'
            ]"
          >
            <FileWarning class="w-4 h-4 flex-shrink-0 text-amber-500 dark:text-amber-400" />
            <span>Pendentes</span>
            <span class="ml-auto text-xs">{{ documentosStore.documentosPorStatus.aguardando_assinatura }}</span>
          </button>

          <button
            @click="selecionarStatus('finalizado')"
            :class="[
              documentosStore.filtroStatus === 'finalizado'
                ? 'bg-emerald-100 text-emerald-900 dark:bg-emerald-900/30 dark:text-emerald-400 font-medium'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700',
              'w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-sm'
            ]"
          >
            <FileCheck class="w-4 h-4 flex-shrink-0 text-emerald-500 dark:text-emerald-400" />
            <span>Finalizados</span>
            <span class="ml-auto text-xs">{{ documentosStore.documentosPorStatus.finalizado }}</span>
          </button>
        </div>
      </div>

      <!-- Divider -->
      <div class="my-4 border-t border-gray-200 dark:border-gray-700"></div>

      <!-- Pastas -->
      <div>
        <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 px-3">
          Pastas
        </h3>
        <div class="space-y-1">
          <!-- Sem Pasta -->
          <button
            @click="selecionarPasta('sem-pasta')"
            :class="[
              documentosStore.pastaAtiva === 'sem-pasta'
                ? 'bg-gray-100 text-gray-900 dark:bg-gray-700 dark:text-gray-100 font-medium'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700',
              'w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-sm'
            ]"
          >
            <Folder class="w-4 h-4 flex-shrink-0 text-gray-400" />
            <span>Sem Pasta</span>
            <span class="ml-auto text-xs">{{ documentosStore.documentos.filter(d => !d.pastaId).length }}</span>
          </button>

          <!-- Pastas Criadas -->
          <button
            v-for="pasta in documentosStore.pastas"
            :key="pasta.id"
            @click="selecionarPasta(pasta.id)"
            :class="[
              documentosStore.pastaAtiva === pasta.id
                ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400 font-medium'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700',
              'w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-sm'
            ]"
          >
            <component
              :is="documentosStore.pastaAtiva === pasta.id ? FolderOpen : Folder"
              class="w-4 h-4 flex-shrink-0"
              :style="{ color: pasta.cor }"
            />
            <span class="truncate">{{ pasta.nome }}</span>
            <span class="ml-auto text-xs flex-shrink-0">{{ contarDocumentosNaPasta(pasta.id) }}</span>
          </button>
        </div>
      </div>

      <!-- Divider -->
      <div class="my-4 border-t border-gray-200 dark:border-gray-700"></div>

      <!-- Etiquetas -->
      <div>
        <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 px-3">
          Etiquetas
        </h3>
        <div v-if="documentosStore.etiquetas.length === 0" class="px-3 text-xs text-gray-500 dark:text-gray-400">
          Nenhuma etiqueta cadastrada.
        </div>
        <div v-else class="space-y-1">
          <button
            v-for="etiqueta in documentosStore.etiquetas"
            :key="etiqueta.id"
            @click="selecionarEtiqueta(etiqueta.id)"
            :class="[
              documentosStore.etiquetaAtiva === etiqueta.id
                ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400 font-medium'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700',
              'w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-sm'
            ]"
          >
            <Tag class="w-4 h-4 flex-shrink-0" :style="{ color: etiqueta.cor }" />
            <span class="truncate">{{ etiqueta.nome }}</span>
            <span class="ml-auto text-xs flex-shrink-0">
              {{ documentosStore.contarDocumentosPorEtiqueta(etiqueta.id) }}
            </span>
          </button>
        </div>
      </div>
    </aside>

    <!-- Área Principal -->
    <main class="flex-1 flex flex-col min-w-0">
      <!-- Header -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-4">
        <!-- Breadcrumbs -->
        <div class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-4">
          <template v-for="(item, index) in breadcrumbs" :key="`breadcrumb-${index}`">
            <span v-if="index > 0" class="text-gray-400 dark:text-gray-600">
              <ChevronRight class="w-4 h-4" />
            </span>
            <span
              :class="[
                index === breadcrumbs.length - 1
                  ? 'text-gray-900 dark:text-gray-100 font-medium'
                  : 'hover:text-gray-900 dark:hover:text-gray-100 cursor-pointer'
              ]"
            >
              {{ item.nome }}
            </span>
          </template>
        </div>

        <!-- Barra de Busca e Ações -->
        <div class="flex flex-col gap-3">
          <!-- Linha 1: Busca e Botão -->
          <div class="flex items-center gap-3">
            <!-- Busca -->
            <div class="flex-1 relative">
              <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                v-model="busca"
                type="text"
                placeholder="Buscar por título, autor ou etiqueta..."
                class="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400"
              />
            </div>

            <!-- Gestor de Templates -->
            <button
              v-if="authStore.hasPermission('ler_docs')"
              @click="$router.push('/documentos/templates')"
              class="flex items-center gap-2 px-4 py-2 bg-purple-100 hover:bg-purple-200 dark:bg-purple-900/30 dark:hover:bg-purple-900/50 text-purple-700 dark:text-purple-400 rounded-lg font-medium transition-colors"
              title="Gerenciar Templates"
            >
              <Settings class="w-5 h-5" />
              Templates
            </button>

            <!-- Botão Novo Documento -->
            <div class="relative">
              <button
                v-if="authStore.hasPermission('criar_docs')"
                @click="novoDocumento()"
                class="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors"
              >
                <FilePlus class="w-5 h-5" />
                Novo Documento
              </button>
            </div>
          </div>

          <!-- Linha 2: Filtros de Período -->
          <div class="flex items-center gap-3">
            <div class="flex items-center gap-2">
              <label class="text-sm text-gray-600 dark:text-gray-400 font-medium">
                Período:
              </label>
              <input
                v-model="dataInicio"
                type="date"
                class="px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400"
              />
              <span class="text-gray-500 dark:text-gray-400">até</span>
              <input
                v-model="dataFim"
                type="date"
                class="px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400"
              />
              <button
                v-if="dataInicio || dataFim"
                @click="dataInicio = ''; dataFim = ''"
                class="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 underline"
              >
                Limpar
              </button>
            </div>
            
            <div class="ml-auto text-sm text-gray-600 dark:text-gray-400">
              {{ documentosExibidos.length }} documento(s)
            </div>
          </div>
        </div>
      </div>

      <!-- Tabela de Documentos -->
      <div class="flex-1 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div class="overflow-x-auto h-full">
          <table class="w-full">
            <thead class="bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Documento
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Status
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Autor
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Última Atualização
                </th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="doc in documentosExibidos"
                :key="doc.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
              >
                <!-- Documento -->
                <td class="px-6 py-4">
                  <div class="flex items-start gap-3">
                    <component
                      :is="getIconeTipo(doc.tipo)"
                      class="w-5 h-5 flex-shrink-0 mt-0.5 text-gray-400 dark:text-gray-500"
                    />
                    <div class="min-w-0">
                      <button
                        @click="editarDocumento(doc.id)"
                        class="text-sm font-medium text-gray-900 dark:text-gray-100 hover:text-primary-600 dark:hover:text-primary-400 text-left line-clamp-2"
                      >
                        {{ doc.titulo }}
                      </button>
                      <div v-if="doc.pasta" class="flex items-center gap-1 mt-1 text-xs text-gray-500 dark:text-gray-400">
                        <Folder class="w-3 h-3" :style="{ color: doc.pasta.cor }" />
                        <span>{{ doc.pasta.nome }}</span>
                      </div>
                      <div v-if="doc.etiquetas.length" class="flex flex-wrap gap-1 mt-2">
                        <span
                          v-for="etiq in doc.etiquetas"
                          :key="etiq.id"
                          class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium text-white"
                          :style="{ backgroundColor: etiq.cor }"
                        >
                          {{ etiq.nome }}
                        </span>
                      </div>
                    </div>
                  </div>
                </td>

                <!-- Status -->
                <td class="px-6 py-4">
                  <span
                    :class="[
                      getStatusBadge(doc.status).classes,
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium'
                    ]"
                  >
                    {{ getStatusBadge(doc.status).label }}
                  </span>
                </td>

                <!-- Autor -->
                <td class="px-6 py-4">
                  <div class="flex items-center gap-2">
                    <img
                      :src="doc.autor.avatar"
                      :alt="doc.autor.nome"
                      class="w-6 h-6 rounded-full"
                    />
                    <span class="text-sm text-gray-900 dark:text-gray-100">
                      {{ doc.autor.nome }}
                    </span>
                  </div>
                </td>

                <!-- Data / auditoria -->
                <td class="px-6 py-4 max-w-[200px]" @click.stop>
                  <RastreabilidadeMeta
                    :rastreabilidade="doc.rastreabilidade"
                    :alvo-auditoria="AUDITORIA_ALVO.documento(doc.id)"
                    historico-titulo="Histórico do documento"
                    compact
                  />
                  <span
                    v-if="!doc.rastreabilidade?.ultimaAcaoEm"
                    class="text-sm text-gray-500 dark:text-gray-400"
                  >
                    {{ formatarData(doc.updatedAt) }}
                  </span>
                </td>

                <!-- Ações -->
                <td class="px-6 py-4 text-right">
                  <div class="relative inline-block">
                    <button
                      @click.stop="toggleMenu(doc.id)"
                      class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded transition-colors"
                    >
                      <MoreVertical class="w-5 h-5" />
                    </button>

                    <!-- Menu Dropdown -->
                    <Transition
                      enter-active-class="transition ease-out duration-100"
                      enter-from-class="transform opacity-0 scale-95"
                      enter-to-class="transform opacity-100 scale-100"
                      leave-active-class="transition ease-in duration-75"
                      leave-from-class="transform opacity-100 scale-100"
                      leave-to-class="transform opacity-0 scale-95"
                    >
                      <div
                        v-if="menuAbertoId === doc.id"
                        v-click-outside="() => menuAbertoId = null"
                        @click.stop
                        class="absolute right-0 mt-2 w-48 rounded-lg shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 z-10"
                      >
                        <div class="py-1">
                          <button
                            v-if="authStore.hasPermission('editar_docs')"
                            @click="editarDocumento(doc.id)"
                            class="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                          >
                            <FileEdit class="w-4 h-4" />
                            Editar
                          </button>

                          <button
                            @click="visualizarPDF(doc.id)"
                            class="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                          >
                            <Eye class="w-4 h-4" />
                            Visualizar PDF
                          </button>

                          <button
                            v-if="authStore.hasPermission('editar_docs')"
                            @click="abrirModalMoverPasta(doc.id)"
                            class="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                          >
                            <FolderInput class="w-4 h-4" />
                            Mover para Pasta
                          </button>

                          <button
                            v-if="authStore.hasPermission('excluir_docs')"
                            @click="excluirDocumento(doc.id)"
                            class="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                          >
                            <Trash2 class="w-4 h-4" />
                            Excluir
                          </button>
                        </div>
                      </div>
                    </Transition>
                  </div>
                </td>
              </tr>

              <!-- Estado Vazio -->
              <tr v-if="documentosExibidos.length === 0">
                <td colspan="5" class="px-6 py-16 text-center">
                  <FileText class="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
                  <p class="text-gray-500 dark:text-gray-400">
                    {{ busca ? 'Nenhum documento encontrado' : 'Nenhum documento nesta pasta' }}
                  </p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>

    <!-- Modal Seletor de Tipo -->
    <TipoDocumentoSelector
      v-if="mostrarSeletorTipo"
      @select="criarDocumentoComTipo"
      @close="mostrarSeletorTipo = false"
    />

    <!-- Modal Mover para Pasta -->
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="mostrarModalMoverPasta"
        class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
        @click.self="cancelarMoverPasta"
      >
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full">
          <!-- Header -->
          <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Mover para Pasta
            </h3>
            <button
              @click="cancelarMoverPasta"
              class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded transition-colors"
            >
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- Conteúdo -->
          <div class="p-6">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Selecione a pasta de destino:
            </label>
            <select
              v-model="pastaDestino"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400"
            >
              <option :value="undefined">Sem pasta</option>
              <option
                v-for="pasta in documentosStore.pastas"
                :key="pasta.id"
                :value="pasta.id"
              >
                {{ pasta.nome }}
              </option>
            </select>
          </div>

          <!-- Footer -->
          <div class="flex items-center justify-end gap-3 p-4 border-t border-gray-200 dark:border-gray-700">
            <button
              @click="cancelarMoverPasta"
              class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              Cancelar
            </button>
            <button
              @click="confirmarMoverPasta"
              class="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors"
            >
              <Check class="w-4 h-4" />
              Mover
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* Diretiva v-click-outside personalizada */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
