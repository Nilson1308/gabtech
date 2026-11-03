<script setup lang="ts">
import type { StatusAtendimento } from '@/types'

interface Props {
  status: StatusAtendimento | string
  variant?: 'status' | 'custom'
  customColor?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'status'
})

const statusConfig: Record<StatusAtendimento, { color: string; label: string }> = {
  aberto: { color: 'bg-blue-100 text-blue-700 border-blue-200', label: 'Aberto' },
  em_andamento: { color: 'bg-yellow-100 text-yellow-700 border-yellow-200', label: 'Em Andamento' },
  aguardando_terceiros: { color: 'bg-purple-100 text-purple-700 border-purple-200', label: 'Aguardando' },
  concluido: { color: 'bg-green-100 text-green-700 border-green-200', label: 'Concluído' },
}

const getStatusClasses = () => {
  if (props.variant === 'status' && props.status in statusConfig) {
    return statusConfig[props.status as StatusAtendimento].color
  }
  return props.customColor || 'bg-gray-100 text-gray-700 border-gray-200'
}

const getStatusLabel = () => {
  if (props.variant === 'status' && props.status in statusConfig) {
    return statusConfig[props.status as StatusAtendimento].label
  }
  return props.status
}
</script>

<template>
  <span 
    :class="getStatusClasses()"
    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border"
  >
    {{ getStatusLabel() }}
  </span>
</template>
