<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import draggable from 'vuedraggable'
import { useAtendimentosStore } from '@/stores/atendimentos'
import { useAuthStore } from '@/stores/auth'
import { useAlertDialog } from '@/composables/useAlertDialog'
import type { Atendimento, StatusAtendimento } from '@/types'
import type { KanbanFiltros } from '@/stores/atendimentos'
import SearchBar from '@/components/common/SearchBar.vue'
import Button from '@/components/common/Button.vue'
import MultiSelectDropdown from '@/components/common/MultiSelectDropdown.vue'
import KanbanColumn from '@/components/atendimentos/KanbanColumn.vue'
import AtendimentoCard from '@/components/atendimentos/AtendimentoCard.vue'
import AtendimentoModal from '@/components/atendimentos/AtendimentoModal.vue'
import {
  MENSAGEM_SAIR_STATUS_ABERTO,
  TITULO_SAIR_STATUS_ABERTO,
} from '@/constants/atendimentos'
import { PERMS } from '@/constants/rbac'
import { Plus, Download } from 'lucide-vue-next'

const atendimentosStore = useAtendimentosStore()
const authStore = useAuthStore()
const { showConfirm, showSuccess, showError } = useAlertDialog()

const podeAlterarStatusKanban = computed(() => authStore.hasPermission(PERMS.atendStatus))

const escopoTodosAtendimentos = computed(() => authStore.hasPermission(PERMS.atendViewAll))

// Estados
const buscaGlobal = ref('')
const macrotemaseSelecionados = ref<string[]>([])
const tagsSelecionadas = ref<string[]>([])
const mostrarModal = ref(false)
const mostrarModalEditar = ref(false)
const atendimentoEditando = ref<Atendimento | null>(null)

const kanbanFiltros = computed<KanbanFiltros>(() => ({
  search: buscaGlobal.value,
  macrotemaIds: macrotemaseSelecionados.value,
  tagIds: tagsSelecionadas.value,
}))

let debounceKanban: ReturnType<typeof setTimeout> | undefined

async function recarregarKanban() {
  await atendimentosStore.fetchKanban(kanbanFiltros.value)
}

onMounted(() => {
  recarregarKanban()
})

watch(kanbanFiltros, () => {
  clearTimeout(debounceKanban)
  debounceKanban = setTimeout(() => {
    recarregarKanban()
  }, 350)
}, { deep: true })

// Configuração das colunas
const colunas = [
  {
    titulo: 'Aberto',
    status: 'aberto' as StatusAtendimento,
    cor: '#3b82f6'
  },
  {
    titulo: 'Em Andamento',
    status: 'em_andamento' as StatusAtendimento,
    cor: '#f59e0b'
  },
  {
    titulo: 'Aguardando Terceiros',
    status: 'aguardando_terceiros' as StatusAtendimento,
    cor: '#8b5cf6'
  },
  {
    titulo: 'Concluído',
    status: 'concluido' as StatusAtendimento,
    cor: '#10b981'
  }
]

const totalFiltrado = computed(() => atendimentosStore.kanbanTotalFiltrado)

function colunaKanban(status: StatusAtendimento) {
  return atendimentosStore.kanbanPorStatus[status]
}

const handleKanbanChange = async (
  event: { added?: { element: Atendimento } },
  statusColuna: StatusAtendimento,
) => {
  const recarregarColunas = async (...statuses: StatusAtendimento[]) => {
    await atendimentosStore.refreshKanbanColunas(statuses, kanbanFiltros.value)
  }

  if (!event.added || !podeAlterarStatusKanban.value) {
    if (event.added && !podeAlterarStatusKanban.value) {
      await recarregarKanban()
    }
    return
  }
  const item = event.added.element
  const statusAnterior = item.status
  if (statusAnterior === statusColuna) {
    return
  }

  if (statusColuna === 'aberto' && statusAnterior !== 'aberto') {
    await recarregarColunas(statusAnterior, statusColuna)
    showError('Não é permitido retornar um atendimento para Aberto.')
    return
  }

  if (statusAnterior === 'aberto' && statusColuna !== 'aberto') {
    const confirmed = await showConfirm(MENSAGEM_SAIR_STATUS_ABERTO, TITULO_SAIR_STATUS_ABERTO)
    if (!confirmed) {
      await recarregarColunas(statusAnterior, statusColuna)
      return
    }
  }

  const ok = await atendimentosStore.updateStatus(item.id, statusColuna, { silent: true })
  if (!ok) {
    await recarregarColunas(statusAnterior, statusColuna)
    showError('Não foi possível atualizar o status.')
    return
  }
  item.status = statusColuna
  await atendimentosStore.refreshKanbanColunas([statusAnterior, statusColuna], kanbanFiltros.value)
}

// Handlers
const handleNovo = () => {
  mostrarModal.value = true
}

const handleSuccess = async () => {
  await recarregarKanban()
}

const handleEditar = async (atendimentoId: string) => {
  const atualizado = await atendimentosStore.getAtendimentoById(atendimentoId, { silent: true })
  if (!atualizado || atualizado.status !== 'aberto') {
    showError('Só é possível editar atendimentos com status Aberto.')
    await recarregarKanban()
    return
  }
  atendimentoEditando.value = atualizado
  mostrarModalEditar.value = true
}

const handleEditado = async () => {
  mostrarModalEditar.value = false
  atendimentoEditando.value = null
  await recarregarKanban()
}

const handleExcluir = async (atendimentoId: string) => {
  if (!authStore.hasPermission(PERMS.atendDelete)) {
    showError('Você não tem permissão para excluir atendimentos.')
    return
  }

  const atendimento =
    Object.values(atendimentosStore.kanbanPorStatus)
      .flatMap(c => c.items)
      .find(a => a.id === atendimentoId)
  
  if (!atendimento) return

  const confirmed = await showConfirm(
    `Tem certeza que deseja excluir o atendimento #${atendimento.protocolo}? Esta ação não pode ser desfeita.`,
    'Excluir Atendimento'
  )

  if (!confirmed) return

  try {
    const sucesso = await atendimentosStore.deleteAtendimento(atendimentoId)
    
    if (sucesso) {
      showSuccess('Atendimento excluído com sucesso!')
    } else {
      showError('Erro ao excluir atendimento.')
    }
  } catch (error) {
    showError('Erro ao excluir atendimento.')
  }
}

const exportandoCsv = ref(false)

const handleExportar = async () => {
  exportandoCsv.value = true
  try {
    const blob = await atendimentosStore.exportAtendimentosCsv({
      search: buscaGlobal.value,
      macrotemaIds: macrotemaseSelecionados.value,
      tagIds: tagsSelecionadas.value,
    })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `atendimentos-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
    showSuccess('Relatório CSV gerado com sucesso.')
  } catch {
    showError('Não foi possível exportar o relatório CSV.')
  } finally {
    exportandoCsv.value = false
  }
}

const limparFiltros = () => {
  buscaGlobal.value = ''
  macrotemaseSelecionados.value = []
  tagsSelecionadas.value = []
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-slate-100">Atendimentos e Protocolos</h2>
        <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
          {{ totalFiltrado }} {{ totalFiltrado === 1 ? 'atendimento' : 'atendimentos' }}
          <span v-if="!escopoTodosAtendimentos" class="block text-xs text-amber-700 dark:text-amber-400 mt-0.5">
            Exibindo apenas protocolos atribuídos a você.
          </span>
        </p>
      </div>

      <div class="flex items-center gap-2">
        <!-- Botão Exportar -->
        <Button
          v-permission="PERMS.atendExport"
          variant="secondary"
          :disabled="exportandoCsv"
          @click="handleExportar"
        >
          <Download class="w-4 h-4" />
          <span class="hidden sm:inline">{{ exportandoCsv ? 'Exportando…' : 'Exportar CSV' }}</span>
        </Button>

        <!-- Botão Novo Atendimento -->
        <Button
          v-permission="PERMS.atendCreate"
          variant="primary"
          @click="handleNovo"
        >
          <Plus class="w-4 h-4" />
          Novo Atendimento
        </Button>
      </div>
    </div>

    <!-- Filtros -->
    <div class="card space-y-4">
      <div class="flex flex-col lg:flex-row gap-4">
        <!-- Busca -->
        <div class="flex-1">
          <SearchBar
            v-model="buscaGlobal"
            placeholder="Buscar por assunto, protocolo ou cidadão..."
          />
        </div>

        <!-- Filtro Macrotemas -->
        <div class="w-full lg:w-64">
          <MultiSelectDropdown
            v-model="macrotemaseSelecionados"
            :options="atendimentosStore.macrotemasDisponiveis"
            placeholder="Todos os macrotemas"
            label="macrotemas"
          />
        </div>

        <!-- Filtro Tags de Serviço -->
        <div class="w-full lg:w-64">
          <MultiSelectDropdown
            v-model="tagsSelecionadas"
            :options="atendimentosStore.tagsAtendimentoDisponiveis"
            placeholder="Todas as tags"
            label="tags"
          />
        </div>

        <!-- Limpar Filtros -->
        <Button
          v-if="buscaGlobal || macrotemaseSelecionados.length > 0 || tagsSelecionadas.length > 0"
          variant="ghost"
          @click="limparFiltros"
        >
          Limpar
        </Button>
      </div>

      <!-- Tags Selecionadas (Visual) -->
      <div v-if="tagsSelecionadas.length > 0" class="flex flex-wrap gap-2">
        <span class="text-sm text-gray-600 dark:text-gray-400">Filtrando por:</span>
        <span
          v-for="tagId in tagsSelecionadas"
          :key="tagId"
          :style="{
            backgroundColor: atendimentosStore.tagsAtendimentoDisponiveis.find(t => t.id === tagId)?.cor + '20',
            color: atendimentosStore.tagsAtendimentoDisponiveis.find(t => t.id === tagId)?.cor,
            borderColor: atendimentosStore.tagsAtendimentoDisponiveis.find(t => t.id === tagId)?.cor
          }"
          class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border"
        >
          {{ atendimentosStore.tagsAtendimentoDisponiveis.find(t => t.id === tagId)?.nome }}
        </span>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="atendimentosStore.kanbanLoading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <template v-else>
      <p
        v-if="!podeAlterarStatusKanban"
        class="text-sm text-gray-500 dark:text-slate-400"
      >
        Seu perfil pode visualizar o quadro, mas não mover cards entre colunas (alteração de status).
      </p>

      <!-- Kanban Board -->
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 items-start">
        <div
          v-for="coluna in colunas"
          :key="coluna.status"
          class="bg-gray-50 dark:bg-slate-800 rounded-lg p-4"
        >
          <KanbanColumn
            :titulo="coluna.titulo"
            :status="coluna.status"
            :atendimentos="colunaKanban(coluna.status).items"
            :cor="coluna.cor"
            :total="colunaKanban(coluna.status).total"
            :has-more="colunaKanban(coluna.status).hasMore"
            :loading-more="colunaKanban(coluna.status).loadingMore"
            @load-more="atendimentosStore.loadMoreKanbanColumn(coluna.status, kanbanFiltros)"
          >
            <draggable
              :list="colunaKanban(coluna.status).items"
              group="atendimentos-kanban"
              item-key="id"
              class="space-y-3 min-h-[120px]"
              ghost-class="opacity-50"
              :disabled="!podeAlterarStatusKanban"
              :class="{ 'cursor-default': !podeAlterarStatusKanban }"
              @change="(evt: { added?: { element: Atendimento } }) => handleKanbanChange(evt, coluna.status)"
            >
              <template #item="{ element }">
                <AtendimentoCard
                  :atendimento="element"
                  @edit="handleEditar"
                  @delete="handleExcluir"
                />
              </template>
            </draggable>
          </KanbanColumn>
        </div>
      </div>
    </template>

    <!-- Modal de Novo Atendimento -->
    <AtendimentoModal
      v-model="mostrarModal"
      @success="handleSuccess"
    />

    <AtendimentoModal
      v-if="atendimentoEditando"
      v-model="mostrarModalEditar"
      :atendimento="atendimentoEditando"
      @success="handleEditado"
    />
  </div>
</template>
