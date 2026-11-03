<script setup lang="ts">
import { ref } from 'vue'
import { X, Table } from 'lucide-vue-next'

interface Emits {
  (e: 'insert', table: { rows: number; cols: number }): void
  (e: 'close'): void
}

const emit = defineEmits<Emits>()

const linhas = ref(3)
const colunas = ref(3)
const comCabecalho = ref(true)

function inserir() {
  emit('insert', { rows: linhas.value, cols: colunas.value })
}

function fechar() {
  emit('close')
}
</script>

<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center gap-2">
          <Table class="w-5 h-5 text-primary-600 dark:text-primary-400" />
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Inserir Tabela
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
      <div class="p-6 space-y-4">
        <!-- Linhas -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Número de Linhas
          </label>
          <input
            v-model.number="linhas"
            type="number"
            min="1"
            max="20"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400"
          />
        </div>

        <!-- Colunas -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Número de Colunas
          </label>
          <input
            v-model.number="colunas"
            type="number"
            min="1"
            max="10"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400"
          />
        </div>

        <!-- Cabeçalho -->
        <div class="flex items-center gap-2">
          <input
            v-model="comCabecalho"
            type="checkbox"
            id="comCabecalho"
            class="w-4 h-4 text-primary-600 bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded focus:ring-primary-500 dark:focus:ring-primary-400"
          />
          <label for="comCabecalho" class="text-sm text-gray-700 dark:text-gray-300">
            Primeira linha como cabeçalho
          </label>
        </div>

        <!-- Preview -->
        <div class="mt-4 p-3 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
          <p class="text-xs text-gray-500 dark:text-gray-400 mb-2">Preview:</p>
          <table class="w-full text-xs border-collapse">
            <thead v-if="comCabecalho">
              <tr>
                <th
                  v-for="col in colunas"
                  :key="col"
                  class="border border-gray-300 dark:border-gray-600 bg-gray-200 dark:bg-gray-700 px-2 py-1"
                >
                  Col {{ col }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in (comCabecalho ? linhas - 1 : linhas)" :key="row">
                <td
                  v-for="col in colunas"
                  :key="col"
                  class="border border-gray-300 dark:border-gray-600 px-2 py-1"
                >
                  &nbsp;
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-end gap-3 p-4 border-t border-gray-200 dark:border-gray-700">
        <button
          @click="fechar"
          class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        >
          Cancelar
        </button>
        <button
          @click="inserir"
          class="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors"
        >
          <Table class="w-4 h-4" />
          Inserir Tabela
        </button>
      </div>
    </div>
  </div>
</template>
