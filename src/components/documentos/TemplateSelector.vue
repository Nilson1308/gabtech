<script setup lang="ts">
import { computed } from 'vue'
import { X, FileText } from 'lucide-vue-next'
import type { Template } from '@/stores/templates'
import type { TipoDocumento } from '@/types'

interface Props {
  templates: Template[]
  tipo: TipoDocumento
}

interface Emits {
  (e: 'select', template: Template): void
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const templatesDoTipo = computed(() => {
  return props.templates.filter(t => t.tipo === props.tipo)
})

function selecionarTemplate(template: Template) {
  emit('select', template)
}

function fechar() {
  emit('close')
}

function getTipoLabel(tipo: TipoDocumento): string {
  const labels: Record<TipoDocumento, string> = {
    oficio: 'Ofício',
    memorando: 'Memorando',
    requerimento: 'Requerimento',
    projeto_lei: 'Projeto de Lei',
    ata: 'Ata',
    declaracao: 'Declaração',
    parecer: 'Parecer',
    relatorio: 'Relatório',
    mocao: 'Moção',
    indicacao: 'Indicação',
    generico: 'Genérico'
  }
  return labels[tipo] || tipo
}
</script>

<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-3xl w-full max-h-[80vh] flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
          Selecionar Template de {{ getTipoLabel(tipo) }}
        </h3>
        <button
          @click="fechar"
          class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded transition-colors"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Lista de Templates -->
      <div class="flex-1 overflow-y-auto p-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            v-for="template in templatesDoTipo"
            :key="template.id"
            @click="selecionarTemplate(template)"
            class="p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-primary-500 dark:hover:border-primary-400 transition-colors text-left group"
          >
            <div class="flex items-start gap-3">
              <div class="p-2 bg-primary-100 dark:bg-primary-900/30 rounded-lg group-hover:bg-primary-200 dark:group-hover:bg-primary-900/50 transition-colors">
                <FileText class="w-6 h-6 text-primary-600 dark:text-primary-400" />
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <h4 class="font-semibold text-gray-900 dark:text-gray-100">
                    {{ template.nome }}
                  </h4>
                  <span
                    v-if="template.isDefault"
                    class="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-xs font-medium rounded"
                  >
                    Padrão
                  </span>
                </div>
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                  {{ template.conteudo.replace(/<[^>]*>/g, '').substring(0, 100) }}...
                </p>
              </div>
            </div>
          </button>
        </div>

        <!-- Estado vazio -->
        <div v-if="templatesDoTipo.length === 0" class="text-center py-12">
          <FileText class="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
          <p class="text-gray-500 dark:text-gray-400">
            Nenhum template disponível para {{ getTipoLabel(tipo) }}
          </p>
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
      </div>
    </div>
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
