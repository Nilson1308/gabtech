<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  label: string
  valor: number | string
  icone: any // Componente Lucide
  cor?: 'blue' | 'green' | 'red' | 'yellow' | 'purple'
  variacao?: {
    valor: number
    tipo: 'aumento' | 'reducao'
    periodo?: string
  }
}

const props = withDefaults(defineProps<Props>(), {
  cor: 'blue'
})

const corConfig = {
  blue: {
    bg: 'bg-blue-100',
    text: 'text-blue-600',
    border: 'border-blue-200'
  },
  green: {
    bg: 'bg-green-100',
    text: 'text-green-600',
    border: 'border-green-200'
  },
  red: {
    bg: 'bg-red-100',
    text: 'text-red-600',
    border: 'border-red-200'
  },
  yellow: {
    bg: 'bg-yellow-100',
    text: 'text-yellow-600',
    border: 'border-yellow-200'
  },
  purple: {
    bg: 'bg-purple-100',
    text: 'text-purple-600',
    border: 'border-purple-200'
  }
}

const config = computed(() => corConfig[props.cor])
</script>

<template>
  <div class="card hover:shadow-md transition-shadow">
    <div class="flex items-start justify-between">
      <div class="flex-1">
        <p class="text-sm font-medium text-gray-600 dark:text-slate-400 mb-2">
          {{ label }}
        </p>
        <p class="text-3xl font-bold text-gray-900 dark:text-slate-100 mb-3">
          {{ valor }}
        </p>
        
        <!-- Variação (opcional) -->
        <div v-if="variacao" class="flex items-center gap-2">
          <span 
            :class="[
              variacao.tipo === 'aumento' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400',
              'text-sm font-medium'
            ]"
          >
            {{ variacao.tipo === 'aumento' ? '+' : '-' }}{{ variacao.valor }}%
          </span>
          <span v-if="variacao.periodo" class="text-xs text-gray-500 dark:text-slate-400">
            {{ variacao.periodo }}
          </span>
        </div>
      </div>
      
      <!-- Ícone -->
      <div 
        :class="[config.bg, config.text, 'w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0']"
      >
        <component :is="icone" class="w-6 h-6" />
      </div>
    </div>
  </div>
</template>
