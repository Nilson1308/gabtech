<script setup lang="ts">
import { ref } from 'vue'
import { X, FileText, Mail, ClipboardList, Scale, FileCheck, FileBadge, FileBarChart, Megaphone, Lightbulb, File } from 'lucide-vue-next'
import type { TipoDocumento } from '@/types'

interface Emits {
  (e: 'select', tipo: TipoDocumento): void
  (e: 'close'): void
}

const emit = defineEmits<Emits>()

const tiposDocumento = [
  {
    tipo: 'oficio' as TipoDocumento,
    nome: 'Ofício',
    descricao: 'Comunicação formal externa',
    icone: FileText,
    cor: '#3b82f6'
  },
  {
    tipo: 'memorando' as TipoDocumento,
    nome: 'Memorando',
    descricao: 'Comunicação interna',
    icone: Mail,
    cor: '#f59e0b'
  },
  {
    tipo: 'requerimento' as TipoDocumento,
    nome: 'Requerimento',
    descricao: 'Solicitações formais',
    icone: ClipboardList,
    cor: '#8b5cf6'
  },
  {
    tipo: 'projeto_lei' as TipoDocumento,
    nome: 'Projeto de Lei',
    descricao: 'Proposições legislativas',
    icone: Scale,
    cor: '#10b981'
  },
  {
    tipo: 'ata' as TipoDocumento,
    nome: 'Ata',
    descricao: 'Registro de reuniões',
    icone: FileText,
    cor: '#6366f1'
  },
  {
    tipo: 'declaracao' as TipoDocumento,
    nome: 'Declaração',
    descricao: 'Declarações oficiais',
    icone: FileCheck,
    cor: '#06b6d4'
  },
  {
    tipo: 'parecer' as TipoDocumento,
    nome: 'Parecer',
    descricao: 'Pareceres técnicos',
    icone: FileBadge,
    cor: '#f97316'
  },
  {
    tipo: 'relatorio' as TipoDocumento,
    nome: 'Relatório',
    descricao: 'Relatórios gerais',
    icone: FileBarChart,
    cor: '#84cc16'
  },
  {
    tipo: 'mocao' as TipoDocumento,
    nome: 'Moção',
    descricao: 'Manifestações formais',
    icone: Megaphone,
    cor: '#ec4899'
  },
  {
    tipo: 'indicacao' as TipoDocumento,
    nome: 'Indicação',
    descricao: 'Sugestões ao Poder Executivo',
    icone: Lightbulb,
    cor: '#facc15'
  },
  {
    tipo: 'generico' as TipoDocumento,
    nome: 'Genérico',
    descricao: 'Documento personalizado',
    icone: File,
    cor: '#6b7280'
  }
]

const tipoSelecionado = ref<TipoDocumento | null>(null)

function selecionar(tipo: TipoDocumento) {
  tipoSelecionado.value = tipo
}

function confirmar() {
  if (tipoSelecionado.value) {
    emit('select', tipoSelecionado.value)
  }
}

function fechar() {
  emit('close')
}
</script>

<template>
  <div
    class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
    @click.self="fechar"
  >
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
        <div>
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Criar Novo Documento
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Selecione o tipo de documento que deseja criar
          </p>
        </div>
        <button
          @click="fechar"
          class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Grid de Tipos -->
      <div class="flex-1 overflow-y-auto p-6">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <button
            v-for="tipo in tiposDocumento"
            :key="tipo.tipo"
            @click="selecionar(tipo.tipo)"
            :class="[
              tipoSelecionado === tipo.tipo
                ? 'border-2 border-primary-500 dark:border-primary-400 bg-primary-50 dark:bg-primary-900/20'
                : 'border-2 border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600',
              'p-4 rounded-lg transition-all text-left group'
            ]"
          >
            <div class="flex items-start gap-3">
              <div
                class="p-3 rounded-lg flex-shrink-0"
                :style="{ backgroundColor: tipo.cor + '20', color: tipo.cor }"
              >
                <component :is="tipo.icone" class="w-6 h-6" />
              </div>
              
              <div class="flex-1 min-w-0">
                <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-1">
                  {{ tipo.nome }}
                </h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  {{ tipo.descricao }}
                </p>
              </div>
            </div>
          </button>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700">
        <button
          @click="fechar"
          class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        >
          Cancelar
        </button>
        <button
          @click="confirmar"
          :disabled="!tipoSelecionado"
          class="px-6 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Criar Documento
        </button>
      </div>
    </div>
  </div>
</template>
