<script setup lang="ts">
import { useRouter } from 'vue-router'
import type { Atendimento } from '@/types'
import { useFormatters } from '@/composables/useFormatters'
import Badge from '@/components/common/Badge.vue'
import { Calendar, ChevronRight, AlertCircle } from 'lucide-vue-next'

interface Props {
  atendimentos: Atendimento[]
}

const props = defineProps<Props>()
const router = useRouter()
const { formatDate } = useFormatters()

const verDetalhes = (id: string) => {
  router.push(`/atendimentos/${id}`)
}
</script>

<template>
  <div class="space-y-4">
    <!-- Estado Vazio -->
    <div v-if="atendimentos.length === 0" class="text-center py-12">
      <p class="text-gray-500 dark:text-slate-400">Nenhum atendimento vinculado a este cidadão</p>
    </div>

    <!-- Timeline -->
    <div v-else class="relative">
      <!-- Linha vertical -->
      <div class="absolute left-5 top-5 bottom-5 w-0.5 bg-gray-200 dark:bg-slate-700"></div>

      <!-- Items -->
      <div
        v-for="atendimento in atendimentos"
        :key="atendimento.id"
        class="relative pl-12 pb-8 last:pb-0"
      >
        <!-- Ponto na timeline -->
        <div 
          class="absolute left-0 top-0 w-10 h-10 rounded-full flex items-center justify-center border-4"
          :style="{ 
            backgroundColor: atendimento.macrotema.cor + '30', 
            borderColor: 'rgb(255 255 255 / var(--tw-border-opacity))'
          }"
          :class="'dark:border-slate-800'"
        >
          <div
            class="w-3 h-3 rounded-full"
            :style="{ backgroundColor: atendimento.macrotema.cor }"
          ></div>
        </div>

        <!-- Card do atendimento -->
        <button
          @click="verDetalhes(atendimento.id)"
          class="w-full text-left p-4 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg hover:border-gray-300 dark:hover:border-slate-600 hover:shadow-sm transition-all group"
        >
          <!-- Header -->
          <div class="flex items-start justify-between gap-3 mb-2">
            <div class="flex-1 min-w-0">
              <h4 class="font-semibold text-gray-900 dark:text-slate-100 truncate group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                {{ atendimento.assunto }}
              </h4>
              <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
                Protocolo: {{ atendimento.protocolo }}
              </p>
            </div>
            <ChevronRight class="w-5 h-5 text-gray-400 dark:text-slate-500 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors flex-shrink-0" />
          </div>

          <!-- Data -->
          <div class="flex items-center gap-2 text-sm text-gray-500 dark:text-slate-400 mb-3">
            <Calendar class="w-4 h-4" />
            {{ formatDate(atendimento.createdAt, true) }}
          </div>

          <!-- Footer: Status + Macrotema + SLA -->
          <div class="flex items-center gap-2 flex-wrap">
            <Badge :status="atendimento.status" />
            
            <span
              :style="{
                backgroundColor: atendimento.macrotema.cor + '20',
                color: atendimento.macrotema.cor
              }"
              class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
            >
              {{ atendimento.macrotema.nome }}
            </span>

            <span
              v-if="atendimento.slaAtrasado"
              class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-700"
            >
              <AlertCircle class="w-3 h-3" />
              SLA Atrasado
            </span>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>
