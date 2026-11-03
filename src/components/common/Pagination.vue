<script setup lang="ts">
import { computed } from 'vue'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'
import type { PaginationMeta } from '@/types'

interface Props {
  meta: PaginationMeta
}

const props = defineProps<Props>()

const emit = defineEmits<{
  changePage: [page: number]
}>()

const startItem = computed(() => {
  return ((props.meta.currentPage - 1) * props.meta.perPage) + 1
})

const endItem = computed(() => {
  return Math.min(props.meta.currentPage * props.meta.perPage, props.meta.totalItems)
})

const goToPage = (page: number) => {
  if (page >= 1 && page <= props.meta.totalPages) {
    emit('changePage', page)
  }
}
</script>

<template>
  <div class="flex items-center justify-between px-4 py-3 border-t border-gray-200 sm:px-6">
    <!-- Info Mobile -->
    <div class="flex-1 flex justify-between sm:hidden">
      <button
        @click="goToPage(meta.currentPage - 1)"
        :disabled="meta.currentPage === 1"
        class="btn btn-secondary"
      >
        Anterior
      </button>
      <button
        @click="goToPage(meta.currentPage + 1)"
        :disabled="meta.currentPage === meta.totalPages"
        class="btn btn-secondary"
      >
        Próxima
      </button>
    </div>

    <!-- Info Desktop -->
    <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
      <div>
        <p class="text-sm text-gray-700">
          Mostrando
          <span class="font-medium">{{ startItem }}</span>
          a
          <span class="font-medium">{{ endItem }}</span>
          de
          <span class="font-medium">{{ meta.totalItems }}</span>
          resultados
        </p>
      </div>
      
      <div class="flex items-center gap-2">
        <button
          @click="goToPage(meta.currentPage - 1)"
          :disabled="meta.currentPage === 1"
          class="btn btn-secondary p-2"
          :class="{ 'opacity-50 cursor-not-allowed': meta.currentPage === 1 }"
        >
          <ChevronLeft class="w-4 h-4" />
        </button>
        
        <span class="px-4 py-2 text-sm font-medium text-gray-700">
          {{ meta.currentPage }} / {{ meta.totalPages }}
        </span>
        
        <button
          @click="goToPage(meta.currentPage + 1)"
          :disabled="meta.currentPage === meta.totalPages"
          class="btn btn-secondary p-2"
          :class="{ 'opacity-50 cursor-not-allowed': meta.currentPage === meta.totalPages }"
        >
          <ChevronRight class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>
