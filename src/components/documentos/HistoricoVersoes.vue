<script setup lang="ts">
import { ref, computed } from 'vue'
import { X, History, Eye, Clock } from 'lucide-vue-next'
import type { Documento } from '@/types'
import * as DiffMatchPatch from 'diff-match-patch'

interface Props {
  documento: Documento
}

interface Emits {
  (e: 'close'): void
  (e: 'restore', versao: number): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const versaoSelecionada = ref<number | null>(null)
const mostrandoDiff = ref(false)

const versoes = computed(() => {
  const lista = [
    {
      numero: props.documento.versaoAtual,
      data: props.documento.updatedAt,
      autor: props.documento.autor,
      mudancas: 'Versão atual',
      conteudo: props.documento.conteudo
    }
  ]

  // Adicionar versões do histórico
  if (props.documento.versoes && props.documento.versoes.length > 0) {
    props.documento.versoes.forEach(v => {
      lista.push({
        numero: v.numeroVersao,
        data: v.createdAt,
        autor: v.autor,
        mudancas: v.mudancas,
        conteudo: v.conteudo
      })
    })
  } else if (props.documento.createdAt !== props.documento.updatedAt) {
    // Criar versão inicial se não houver histórico
    lista.push({
      numero: 1,
      data: props.documento.createdAt,
      autor: props.documento.autor,
      mudancas: 'Versão inicial',
      conteudo: '<p>Versão inicial do documento</p>'
    })
  }

  return lista.sort((a, b) => b.numero - a.numero)
})

const diffHtml = computed(() => {
  if (!versaoSelecionada.value || !mostrandoDiff.value) return ''
  
  const versaoAtual = versoes.value.find(v => v.numero === props.documento.versaoAtual)
  const versaoComparar = versoes.value.find(v => v.numero === versaoSelecionada.value)
  
  if (!versaoAtual || !versaoComparar) return ''
  
  const dmp = new DiffMatchPatch.diff_match_patch()
  const diff = dmp.diff_main(versaoComparar.conteudo, versaoAtual.conteudo)
  dmp.diff_cleanupSemantic(diff)
  
  return dmp.diff_prettyHtml(diff)
})

function selecionarVersao(numero: number) {
  versaoSelecionada.value = numero
  mostrandoDiff.value = false
}

function visualizarDiff() {
  mostrandoDiff.value = !mostrandoDiff.value
}

function restaurarVersao(numero: number) {
  if (confirm(`Deseja restaurar o documento para a versão ${numero}? Isso criará uma nova versão com o conteúdo antigo.`)) {
    emit('restore', numero)
  }
}

function fechar() {
  emit('close')
}

function formatarData(data: string) {
  return new Date(data).toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-5xl w-full max-h-[90vh] flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center gap-2">
          <History class="w-5 h-5 text-primary-600 dark:text-primary-400" />
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Histórico de Versões
          </h3>
        </div>
        <button
          @click="fechar"
          class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded transition-colors"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Conteúdo -->
      <div class="flex-1 overflow-hidden flex">
        <!-- Lista de Versões -->
        <div class="w-80 border-r border-gray-200 dark:border-gray-700 overflow-y-auto">
          <div class="p-3 space-y-2">
            <button
              v-for="versao in versoes"
              :key="versao.numero"
              @click="selecionarVersao(versao.numero)"
              :class="[
                versaoSelecionada === versao.numero
                  ? 'bg-primary-50 dark:bg-primary-900/30 border-primary-500 dark:border-primary-400'
                  : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600',
                'w-full p-3 border-2 rounded-lg transition-colors text-left'
              ]"
            >
              <div class="flex items-start justify-between gap-2 mb-2">
                <span class="font-semibold text-gray-900 dark:text-gray-100">
                  Versão {{ versao.numero }}
                </span>
                <span
                  v-if="versao.numero === documento.versaoAtual"
                  class="px-2 py-0.5 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 text-xs font-medium rounded"
                >
                  Atual
                </span>
              </div>
              
              <div class="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400 mb-1">
                <img
                  :src="versao.autor.avatar"
                  :alt="versao.autor.nome"
                  class="w-4 h-4 rounded-full"
                />
                <span>{{ versao.autor.nome }}</span>
              </div>
              
              <div class="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-500">
                <Clock class="w-3 h-3" />
                {{ formatarData(versao.data) }}
              </div>
              
              <p class="text-xs text-gray-600 dark:text-gray-400 mt-2 italic">
                {{ versao.mudancas }}
              </p>
            </button>
          </div>
        </div>

        <!-- Preview / Diff -->
        <div class="flex-1 overflow-y-auto p-6">
          <div v-if="versaoSelecionada">
            <!-- Ações -->
            <div class="flex items-center gap-3 mb-4">
              <button
                v-if="versaoSelecionada !== documento.versaoAtual"
                @click="visualizarDiff"
                class="flex items-center gap-2 px-3 py-2 bg-blue-100 hover:bg-blue-200 dark:bg-blue-900/30 dark:hover:bg-blue-900/50 text-blue-700 dark:text-blue-400 rounded-lg transition-colors text-sm font-medium"
              >
                <Eye class="w-4 h-4" />
                {{ mostrandoDiff ? 'Ver Conteúdo' : 'Ver Diferenças' }}
              </button>

              <button
                v-if="versaoSelecionada !== documento.versaoAtual && documento.status === 'rascunho'"
                @click="restaurarVersao(versaoSelecionada)"
                class="flex items-center gap-2 px-3 py-2 bg-amber-100 hover:bg-amber-200 dark:bg-amber-900/30 dark:hover:bg-amber-900/50 text-amber-700 dark:text-amber-400 rounded-lg transition-colors text-sm font-medium"
              >
                <History class="w-4 h-4" />
                Restaurar Esta Versão
              </button>
            </div>

            <!-- Diff View -->
            <div v-if="mostrandoDiff && versaoSelecionada !== documento.versaoAtual" class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
              <h4 class="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3">
                Diferenças entre Versão {{ versaoSelecionada }} e Versão Atual ({{ documento.versaoAtual }})
              </h4>
              <div
                class="prose dark:prose-invert max-w-none text-sm"
                v-html="diffHtml"
              />
              <div class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded border border-blue-200 dark:border-blue-800">
                <p class="text-xs text-blue-700 dark:text-blue-400">
                  <strong>Legenda:</strong>
                  <span class="inline-block ml-2 px-2 py-0.5 bg-green-200 text-green-900 rounded">Verde = Adicionado</span>
                  <span class="inline-block ml-2 px-2 py-0.5 bg-red-200 text-red-900 rounded">Vermelho = Removido</span>
                </p>
              </div>
            </div>

            <!-- Content View -->
            <div v-else class="bg-white dark:bg-gray-50 rounded-lg p-8 shadow-sm">
              <div
                v-html="versoes.find(v => v.numero === versaoSelecionada)?.conteudo"
                style="font-family: Arial, sans-serif; color: #1f2937; line-height: 1.6;"
              />
            </div>
          </div>

          <div v-else class="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
            <div class="text-center">
              <History class="w-12 h-12 mx-auto mb-4 text-gray-300 dark:text-gray-600" />
              <p>Selecione uma versão para visualizar</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-end gap-3 p-4 border-t border-gray-200 dark:border-gray-700">
        <button
          @click="fechar"
          class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        >
          Fechar
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Estilos para o diff */
:deep(ins) {
  background-color: #bbf7d0;
  color: #166534;
  text-decoration: none;
}

:deep(del) {
  background-color: #fecaca;
  color: #991b1b;
  text-decoration: line-through;
}

.dark :deep(ins) {
  background-color: #166534;
  color: #bbf7d0;
}

.dark :deep(del) {
  background-color: #991b1b;
  color: #fecaca;
}
</style>
