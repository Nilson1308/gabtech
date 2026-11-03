<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useCrmStore } from '@/stores/crm'
import type { Tag } from '@/types'
import SearchBar from '@/components/common/SearchBar.vue'
import Button from '@/components/common/Button.vue'
import CidadaoTable from '@/components/crm/CidadaoTable.vue'
import CidadaoModal from '@/components/crm/CidadaoModal.vue'
import Pagination from '@/components/common/Pagination.vue'
import { PERMS } from '@/constants/rbac'
import { Plus, Download, Filter } from 'lucide-vue-next'

const crmStore = useCrmStore()

// Estados
const buscaGlobal = ref('')
const tagSelecionada = ref<Tag | null>(null)
const mostrarModal = ref(false)
const paginaAtual = ref(1)
const itensPorPagina = ref(10)

// Dados
const dadosPaginados = ref<any>({ data: [], meta: { currentPage: 1, perPage: 10, totalPages: 1, totalItems: 0 } })

// Computed
const cidadaosFiltrados = computed(() => {
  let resultado = crmStore.cidadaos

  // Filtro de busca global
  if (buscaGlobal.value) {
    const query = buscaGlobal.value.toLowerCase()
    resultado = resultado.filter(cidadao =>
      cidadao.nome.toLowerCase().includes(query) ||
      cidadao.telefone.includes(query) ||
      cidadao.email?.toLowerCase().includes(query) ||
      cidadao.cpf?.includes(query) ||
      cidadao.bairro?.toLowerCase().includes(query)
    )
  }

  if (tagSelecionada.value) {
    const tagId = tagSelecionada.value.id
    resultado = resultado.filter(cidadao => crmStore.cidadaoTemTag(cidadao, tagId))
  }

  return resultado
})

// Carregar dados
onMounted(async () => {
  await carregarDados()
})

const carregarDados = async () => {
  const response = await crmStore.fetchCidadaos(paginaAtual.value, itensPorPagina.value)
  dadosPaginados.value = response
}

// Handlers
const handlePageChange = async (page: number) => {
  paginaAtual.value = page
  await carregarDados()
}

const handleNovoCidadao = () => {
  mostrarModal.value = true
}

const handleSuccess = async () => {
  await carregarDados()
}

const handleExportar = () => {
  // Mock de exportação
  const csv = cidadaosFiltrados.value.map(c => {
    return [
      c.nome,
      c.cpf || '',
      c.telefone,
      c.email || '',
      c.bairro || '',
      c.perfis_profissionais?.map(p => p.cargo).join('; ') || ''
    ].join(',')
  }).join('\n')

  const header = 'Nome,CPF,Telefone,Email,Bairro,Perfis\n'
  const blob = new Blob([header + csv], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `cidadaos-${new Date().toISOString().split('T')[0]}.csv`
  a.click()
}

const limparFiltros = () => {
  buscaGlobal.value = ''
  tagSelecionada.value = null
}

const totalFiltrado = computed(() => cidadaosFiltrados.value.length)
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-slate-100">Gestão de Cidadãos</h2>
        <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
          {{ totalFiltrado }} {{ totalFiltrado === 1 ? 'cidadão' : 'cidadãos' }} cadastrados
        </p>
      </div>

      <div class="flex items-center gap-2">
        <!-- Botão Exportar CSV -->
        <Button
          v-permission="PERMS.crmExport"
          variant="secondary"
          @click="handleExportar"
        >
          <Download class="w-4 h-4" />
          <span class="hidden sm:inline">Exportar CSV</span>
        </Button>

        <!-- Botão Novo Contato -->
        <Button
          v-permission="PERMS.crmCreate"
          variant="primary"
          @click="handleNovoCidadao"
        >
          <Plus class="w-4 h-4" />
          Novo Contato
        </Button>
      </div>
    </div>

    <!-- Toolbar -->
    <div class="card">
      <div class="flex flex-col lg:flex-row gap-4">
        <!-- Busca Global -->
        <div class="flex-1">
          <SearchBar
            v-model="buscaGlobal"
            placeholder="Buscar por nome, CPF, telefone, email ou bairro..."
          />
        </div>

        <!-- Filtro por Tag -->
        <div class="w-full lg:w-64">
          <div class="relative">
            <Filter class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
            <select
              v-model="tagSelecionada"
              class="input pl-10"
            >
              <option :value="null">Todas as tags</option>
              <option
                v-for="tag in crmStore.tagsDisponiveis"
                :key="tag.id"
                :value="tag"
              >
                {{ tag.nome }}
              </option>
            </select>
          </div>
        </div>

        <!-- Limpar Filtros -->
        <Button
          v-if="buscaGlobal || tagSelecionada"
          variant="ghost"
          @click="limparFiltros"
          class="whitespace-nowrap"
        >
          Limpar filtros
        </Button>
      </div>
    </div>

    <!-- Tabela -->
    <div class="card p-0">
      <CidadaoTable
        :cidadaos="cidadaosFiltrados.slice((paginaAtual - 1) * itensPorPagina, paginaAtual * itensPorPagina)"
        :loading="crmStore.loading"
      />

      <!-- Paginação -->
      <Pagination
        :meta="{
          currentPage: paginaAtual,
          perPage: itensPorPagina,
          totalPages: Math.ceil(cidadaosFiltrados.length / itensPorPagina),
          totalItems: cidadaosFiltrados.length
        }"
        @change-page="handlePageChange"
      />
    </div>

    <!-- Modal de Criação -->
    <CidadaoModal
      v-model="mostrarModal"
      @success="handleSuccess"
    />
  </div>
</template>
