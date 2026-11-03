<script setup lang="ts">
import { computed } from 'vue'
import { useFormatters } from '@/composables/useFormatters'

interface Props {
  nome: string
  avatar?: string
  tamanho?: 'sm' | 'md' | 'lg' | 'xl'
}

const props = withDefaults(defineProps<Props>(), {
  tamanho: 'md'
})

const { getInitials } = useFormatters()

const iniciais = computed(() => getInitials(props.nome))

const tamanhoClasses = {
  sm: 'w-8 h-8 text-xs',
  md: 'w-10 h-10 text-sm',
  lg: 'w-12 h-12 text-base',
  xl: 'w-16 h-16 text-lg',
}
</script>

<template>
  <div 
    v-if="avatar"
    :class="tamanhoClasses[tamanho]"
    class="rounded-full overflow-hidden flex-shrink-0"
  >
    <img :src="avatar" :alt="nome" class="w-full h-full object-cover" />
  </div>
  
  <div 
    v-else
    :class="tamanhoClasses[tamanho]"
    class="rounded-full bg-primary-600 text-white flex items-center justify-center font-semibold flex-shrink-0"
  >
    {{ iniciais }}
  </div>
</template>
