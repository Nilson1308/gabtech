<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useCrmStore } from '@/stores/crm'
import type { Cidadao, PaginatedResponse } from '@/types'
import SearchBar from '@/components/common/SearchBar.vue'
import Button from '@/components/common/Button.vue'
import CidadaoTable from '@/components/crm/CidadaoTable.vue'
import CidadaoModal from '@/components/crm/CidadaoModal.vue'
import Pagination from '@/components/common/Pagination.vue'
import { PERMS } from '@/constants/rbac'
import { Plus, Download, Filter } from 'lucide-vue-next'

const crmStore = useCrmStore()

const buscaGlobal = ref('')
const tagIdFiltro = ref('')
const mostrarModal = ref(false)
const paginaAtual = ref(1)
const itensPorPagina = ref(25)
const exportando = ref(false)

const dadosPaginados = ref<PaginatedResponse<Cidadao>>({
  data: [],
  meta: { currentPage: 1, perPage: 25, totalPages: 1, totalItems: 0 },
})

let debounceBusca: ReturnType<typeof setTimeout> | undefined

const filtrosAtuais = () => ({
  search: buscaGlobal.value,
  tagId: tagIdFiltro.value || null,
})

const carregarDados = async () => {
  const response = await crmStore.fetchCidadaos(
    paginaAtual.value,
    itensPorPagina.value,
    filtrosAtuais(),
  )
  dadosPaginados.value = response
}

onMounted(async () => {
  await crmStore.fetchTags()
  await carregarDados()
})

watch(tagIdFiltro, async () => {
  paginaAtual.value = 1
  await carregarDados()
})

watch(buscaGlobal, () => {
  clearTimeout(debounceBusca)
  debounceBusca = setTimeout(async () => {
    paginaAtual.value = 1
    await carregarDados()
  }, 350)
})

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

const handleExportar = async () => {
  exportando.value = true
  try {
    const linhas: string[] = []
    const header = 'Nome,CPF,Telefone,Email,Bairro,Perfis\n'
    await crmStore.iterarCidadaosFiltrados(filtrosAtuais(), batch => {
      for (const c of batch) {
        linhas.push(
          [
            c.nome,
            c.cpf || '',
            c.telefone,
            c.email || '',
            c.bairro || '',
            c.perfis_profissionais?.map(p => p.cargo).join('; ') || '',
          ].join(','),
        )
      }
    })
    const blob = new Blob([header + linhas.join('\n')], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `cidadaos-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  } finally {
    exportando.value = false
  }
}

const limparFiltros = async () => {
  buscaGlobal.value = ''
  tagIdFiltro.value = ''
  paginaAtual.value = 1
  await carregarDados()
}

const totalFiltrado = computed(() => dadosPaginados.value.meta.totalItems)
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-slate-100">Gestão de Cidadãos</h2>
        <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
          {{ totalFiltrado }} {{ totalFiltrado === 1 ? 'cidadão' : 'cidadãos' }}
          <span v-if="buscaGlobal || tagIdFiltro"> (filtro aplicado)</span>
        </p>
      </div>

      <div class="flex items-center gap-2">
        <Button
          v-permission="PERMS.crmExport"
          variant="secondary"
          :disabled="exportando"
          @click="handleExportar"
        >
          <Download class="w-4 h-4" />
          <span class="hidden sm:inline">{{ exportando ? 'Exportando…' : 'Exportar CSV' }}</span>
        </Button>

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
        <div class="flex-1">
          <SearchBar
            v-model="buscaGlobal"
            placeholder="Buscar por nome, CPF, telefone, email ou bairro..."
          />
        </div>

        <div class="w-full lg:w-64">
          <div class="relative">
            <Filter class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
            <select v-model="tagIdFiltro" class="input pl-10">
              <option value="">Todas as tags</option>
              <option v-for="tag in crmStore.tagsDisponiveis" :key="tag.id" :value="tag.id">
                {{ tag.nome }}
              </option>
            </select>
          </div>
        </div>

        <Button
          v-if="buscaGlobal || tagIdFiltro"
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
      <CidadaoTable :cidadaos="dadosPaginados.data" :loading="crmStore.loading" />

      <Pagination :meta="dadosPaginados.meta" @change-page="handlePageChange" />
    </div>

    <CidadaoModal v-model="mostrarModal" @success="handleSuccess" />
  </div>
</template>
