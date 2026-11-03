<script setup lang="ts">
import { Loader2 } from 'lucide-vue-next'

interface Props {
  tamanho?: 'sm' | 'md' | 'lg'
  texto?: string
}

const props = withDefaults(defineProps<Props>(), {
  tamanho: 'md'
})

const tamanhoClasses = {
  sm: 'w-4 h-4',
  md: 'w-8 h-8',
  lg: 'w-12 h-12',
}
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-3">
    <Loader2 :class="tamanhoClasses[tamanho]" class="text-primary-600 animate-spin" />
    <p v-if="texto" class="text-sm text-gray-600">{{ texto }}</p>
  </div>
</template>
