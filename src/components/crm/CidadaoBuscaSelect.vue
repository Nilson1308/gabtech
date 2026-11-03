<script setup lang="ts">
import { ref, watch } from 'vue'
import { useCrmStore } from '@/stores/crm'
import { ApiError } from '@/services/api'
import type { Cidadao } from '@/types'
import { Loader2, Search, User, X } from 'lucide-vue-next'

const model = defineModel<string | null>({ default: null })

interface Props {
  label?: string
  placeholder?: string
  /** Oculta chip do selecionado (busca one-shot) */
  semChip?: boolean
  searchOptions?: {
    anexoCategoria?: string
    curriculoTagIds?: string[]
  }
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Nome, CPF ou telefone (mín. 2 caracteres)',
})

const emit = defineEmits<{
  select: [cidadao: Cidadao]
  clear: []
}>()

const crmStore = useCrmStore()

const busca = ref('')
const resultados = ref<Cidadao[]>([])
const buscando = ref(false)
const erro = ref('')
const selecionado = ref<Cidadao | null>(null)

let debounceTimer: ReturnType<typeof setTimeout> | undefined
let buscaSeq = 0

watch(
  () => model.value,
  async id => {
    if (!id) {
      selecionado.value = null
      return
    }
    if (selecionado.value?.id === id) return
    const c = await crmStore.getCidadaoById(id)
    if (c) selecionado.value = c
  },
  { immediate: true },
)

function mensagemErro(e: unknown): string {
  if (e instanceof ApiError) {
    if (e.status === 403) return 'Sem permissão para consultar cidadãos.'
    if (e.status === 401) return 'Sessão expirada. Faça login novamente.'
  }
  return 'Não foi possível buscar cidadãos.'
}

watch(busca, query => {
  clearTimeout(debounceTimer)
  const trimmed = query.trim()
  if (trimmed.length < 2) {
    resultados.value = []
    erro.value = ''
    return
  }
  buscando.value = true
  erro.value = ''
  const seq = ++buscaSeq
  debounceTimer = setTimeout(async () => {
    try {
      const lista = await crmStore.searchCidadaos(trimmed, 15, props.searchOptions)
      if (seq !== buscaSeq) return
      resultados.value = lista
    } catch (e) {
      if (seq !== buscaSeq) return
      resultados.value = []
      erro.value = mensagemErro(e)
    } finally {
      if (seq === buscaSeq) buscando.value = false
    }
  }, 300)
})

function escolher(c: Cidadao) {
  selecionado.value = c
  model.value = c.id
  busca.value = ''
  resultados.value = []
  emit('select', c)
}

function limpar() {
  selecionado.value = null
  model.value = null
  busca.value = ''
  resultados.value = []
  emit('clear')
}

function iniciais(nome: string) {
  return nome.trim().charAt(0).toUpperCase() || '?'
}

function subtitulo(c: Cidadao) {
  const partes = [c.telefone, c.cpf, c.bairro].filter(Boolean)
  return partes.join(' · ')
}
</script>

<template>
  <div class="space-y-2">
    <label v-if="label" class="label">{{ label }}</label>

    <div
      v-if="selecionado && !semChip"
      class="flex items-center gap-3 p-3 rounded-lg border border-primary-200 dark:border-primary-800 bg-primary-50/50 dark:bg-primary-950/30"
    >
      <div
        class="w-10 h-10 rounded-full bg-primary-100 dark:bg-primary-900/40 flex items-center justify-center text-primary-700 dark:text-primary-300 font-semibold shrink-0"
      >
        <img
          v-if="selecionado.avatar"
          :src="selecionado.avatar"
          :alt="selecionado.nome"
          class="w-10 h-10 rounded-full object-cover"
        />
        <span v-else>{{ iniciais(selecionado.nome) }}</span>
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-sm font-medium text-gray-900 dark:text-slate-100 truncate">
          {{ selecionado.nome }}
        </p>
        <p class="text-xs text-gray-500 dark:text-slate-400 truncate">
          {{ subtitulo(selecionado) }}
        </p>
      </div>
      <button
        type="button"
        class="p-1.5 rounded-lg text-gray-500 hover:bg-white/80 dark:hover:bg-slate-800"
        title="Trocar cidadão"
        @click="limpar"
      >
        <X class="w-4 h-4" />
      </button>
    </div>

    <div v-else class="relative">
      <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-slate-500" />
      <input
        v-model="busca"
        type="search"
        class="input pl-9"
        :placeholder="placeholder"
        autocomplete="off"
      />
    </div>

    <p v-if="buscando" class="text-xs text-gray-500 dark:text-slate-400 flex items-center gap-2">
      <Loader2 class="w-3.5 h-3.5 animate-spin" />
      Buscando no CRM…
    </p>
    <p v-else-if="erro" class="text-xs text-red-600 dark:text-red-400">{{ erro }}</p>
    <p
      v-else-if="busca.trim().length >= 2 && !buscando && resultados.length === 0"
      class="text-xs text-gray-500 dark:text-slate-400"
    >
      Nenhum cidadão encontrado.
    </p>

    <div
      v-if="resultados.length > 0"
      class="border border-gray-200 dark:border-slate-700 rounded-lg overflow-hidden bg-white dark:bg-slate-800 max-h-52 overflow-y-auto shadow-sm"
    >
      <button
        v-for="c in resultados"
        :key="c.id"
        type="button"
        class="w-full px-3 py-2.5 text-left hover:bg-gray-50 dark:hover:bg-slate-700/80 transition-colors flex items-center gap-3 border-b border-gray-100 dark:border-slate-700 last:border-0"
        @click="escolher(c)"
      >
        <div
          class="w-9 h-9 rounded-full bg-gray-100 dark:bg-slate-700 flex items-center justify-center text-gray-700 dark:text-slate-200 font-semibold text-sm shrink-0"
        >
          <img v-if="c.avatar" :src="c.avatar" :alt="c.nome" class="w-9 h-9 rounded-full object-cover" />
          <User v-else-if="!c.nome" class="w-4 h-4" />
          <span v-else>{{ iniciais(c.nome) }}</span>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-900 dark:text-slate-100 truncate">{{ c.nome }}</p>
          <p class="text-xs text-gray-500 dark:text-slate-400 truncate">{{ subtitulo(c) }}</p>
        </div>
      </button>
    </div>
  </div>
</template>
