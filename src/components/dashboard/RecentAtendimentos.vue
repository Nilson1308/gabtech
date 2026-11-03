<script setup lang="ts">
import { useRouter } from 'vue-router'
import type { Atendimento } from '@/types'
import { useFormatters } from '@/composables/useFormatters'
import Badge from '@/components/common/Badge.vue'
import { Clock, AlertCircle, ChevronRight } from 'lucide-vue-next'

interface Props {
  atendimentos: Atendimento[]
}

const props = defineProps<Props>()
const router = useRouter()
const { formatRelativeTime } = useFormatters()

const verDetalhes = (id: string) => {
  router.push(`/atendimentos/${id}`)
}
</script>

<template>
  <div class="card">
    <div class="flex items-center justify-between mb-4">
      <div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-slate-100">
          Últimos Atendimentos
        </h3>
        <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
          Protocolos recentes do sistema
        </p>
      </div>
      <button
        @click="router.push('/atendimentos')"
        class="text-sm font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 transition-colors"
      >
        Ver todos
      </button>
    </div>

    <!-- Estado Vazio -->
    <div v-if="atendimentos.length === 0" class="py-12 text-center">
      <p class="text-gray-500 dark:text-slate-400 text-sm">Nenhum atendimento encontrado</p>
    </div>

    <!-- Lista de Atendimentos -->
    <div v-else class="divide-y divide-gray-100 dark:divide-slate-700">
      <button
        v-for="atendimento in atendimentos"
        :key="atendimento.id"
        @click="verDetalhes(atendimento.id)"
        class="w-full text-left py-4 hover:bg-gray-50 dark:hover:bg-slate-700 -mx-6 px-6 transition-colors group"
      >
        <div class="flex items-start gap-4">
          <!-- Ícone/Cor do Macrotema -->
          <div 
            :style="{ backgroundColor: atendimento.macrotema.cor + '20', borderColor: atendimento.macrotema.cor }"
            class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 border-2"
          >
            <div 
              :style="{ backgroundColor: atendimento.macrotema.cor }"
              class="w-2 h-2 rounded-full"
            />
          </div>

          <!-- Conteúdo -->
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between gap-3 mb-1">
              <h4 class="font-semibold text-gray-900 dark:text-slate-100 truncate">
                {{ atendimento.assunto }}
              </h4>
              <ChevronRight class="w-4 h-4 text-gray-400 dark:text-slate-500 group-hover:text-gray-600 dark:group-hover:text-slate-400 transition-colors flex-shrink-0" />
            </div>

            <div class="flex items-center gap-2 text-sm text-gray-600 dark:text-slate-400 mb-2">
              <span class="truncate">{{ atendimento.cidadao.nome }}</span>
              <span class="text-gray-400 dark:text-slate-500">•</span>
              <span class="flex items-center gap-1 text-xs">
                <Clock class="w-3 h-3" />
                {{ formatRelativeTime(atendimento.createdAt) }}
              </span>
            </div>

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

              <!-- Indicador de SLA Atrasado -->
              <span 
                v-if="atendimento.slaAtrasado"
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-700"
              >
                <AlertCircle class="w-3 h-3" />
                SLA Atrasado
              </span>
            </div>
          </div>
        </div>
      </button>
    </div>
  </div>
</template>
