<script setup lang="ts">
import { computed } from 'vue'
import type { DadosGraficoMacrotema } from '@/types'

interface Props {
  dados: DadosGraficoMacrotema[]
}

const props = defineProps<Props>()

const maxValor = computed(() => {
  if (props.dados.length === 0) return 1
  return Math.max(...props.dados.map(d => d.quantidade))
})

const dadosOrdenados = computed(() => {
  return [...props.dados].sort((a, b) => b.quantidade - a.quantidade)
})
</script>

<template>
  <div class="card">
    <div class="mb-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-slate-100">
        Atendimentos por Macrotema
      </h3>
      <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
        Distribuição dos {{ dados.reduce((acc, d) => acc + d.quantidade, 0) }} atendimentos
      </p>
    </div>

    <!-- Estado Vazio -->
    <div v-if="dados.length === 0" class="py-12 text-center">
      <p class="text-gray-500 dark:text-slate-400">Nenhum dado disponível</p>
    </div>

    <!-- Gráfico de Barras -->
    <div v-else class="space-y-4">
      <div 
        v-for="item in dadosOrdenados" 
        :key="item.macrotema"
        class="flex items-center gap-4"
      >
        <!-- Label do Macrotema -->
        <div class="w-32 text-sm font-medium text-gray-700 dark:text-slate-300 flex-shrink-0">
          {{ item.macrotema }}
        </div>
        
        <!-- Barra -->
        <div class="flex-1 bg-gray-100 dark:bg-slate-700 rounded-full h-10 relative overflow-hidden">
          <div 
            :style="{ 
              width: `${(item.quantidade / maxValor) * 100}%`,
              backgroundColor: item.cor
            }"
            class="h-full rounded-full transition-all duration-700 ease-out flex items-center justify-end pr-3"
          >
            <span class="text-xs font-semibold text-white drop-shadow">
              {{ item.quantidade }}
            </span>
          </div>
        </div>
        
        <!-- Porcentagem -->
        <div class="w-12 text-sm text-gray-600 dark:text-slate-400 text-right flex-shrink-0">
          {{ Math.round((item.quantidade / dados.reduce((acc, d) => acc + d.quantidade, 0)) * 100) }}%
        </div>
      </div>
    </div>
  </div>
</template>
