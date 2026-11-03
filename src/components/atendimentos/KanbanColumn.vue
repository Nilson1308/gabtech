<script setup lang="ts">
import { computed } from 'vue'
import type { Atendimento, StatusAtendimento } from '@/types'
import Button from '@/components/common/Button.vue'

interface Props {
  titulo: string
  status: StatusAtendimento
  atendimentos: Atendimento[]
  cor: string
  total: number
  hasMore: boolean
  loadingMore: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'load-more': []
}>()

const restantes = computed(() => Math.max(0, props.total - props.atendimentos.length))
</script>

<template>
  <div class="flex flex-col">
    <!-- Header da Coluna -->
    <div class="flex items-center justify-between mb-4 pb-3 border-b-2" :style="{ borderColor: cor }">
      <div class="flex items-center gap-2">
        <div class="w-3 h-3 rounded-full" :style="{ backgroundColor: cor }"></div>
        <h3 class="font-semibold text-gray-900 dark:text-slate-100">{{ titulo }}</h3>
      </div>
      <span
        class="px-2 py-0.5 rounded-full text-xs font-medium"
        :style="{ backgroundColor: cor + '20', color: cor }"
      >
        {{ total }}
      </span>
    </div>

    <!-- Cards -->
    <div class="space-y-3">
      <slot />

      <div v-if="atendimentos.length === 0 && !loadingMore" class="text-center py-8">
        <p class="text-sm text-gray-400 dark:text-slate-500">Nenhum atendimento</p>
      </div>

      <div v-if="hasMore && atendimentos.length > 0" class="pt-1">
        <Button
          variant="ghost"
          class="w-full text-sm"
          :disabled="loadingMore"
          @click="emit('load-more')"
        >
          <span v-if="loadingMore">Carregando…</span>
          <span v-else>
            Carregar mais
            <template v-if="restantes > 0"> ({{ restantes }} restantes)</template>
          </span>
        </Button>
      </div>
    </div>
  </div>
</template>
