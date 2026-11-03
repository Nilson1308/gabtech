<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAtendimentosStore } from '@/stores/atendimentos'
import { useCrmStore } from '@/stores/crm'
import { useAnalyticsStore } from '@/stores/analytics'
import MetricCard from '@/components/dashboard/MetricCard.vue'
import MacrotemaChart from '@/components/dashboard/MacrotemaChart.vue'
import QuickActions from '@/components/dashboard/QuickActions.vue'
import RecentAtendimentos from '@/components/dashboard/RecentAtendimentos.vue'
import { PERMS } from '@/constants/rbac'
import { Sparkles, Inbox, AlertCircle, Users, TrendingUp, Activity, AlertTriangle, CheckCircle, Clock, ArrowRight, UserPlus, Calendar, FileCheck } from 'lucide-vue-next'

const authStore = useAuthStore()
const atendimentosStore = useAtendimentosStore()
const crmStore = useCrmStore()
const analyticsStore = useAnalyticsStore()

const visaoExecutiva = ref(false)

const temPermissaoOperacional = computed(() => authStore.hasPermission(PERMS.dashboardOperacional))
const temPermissaoExecutiva = computed(() => authStore.hasPermission(PERMS.dashboard))
const escopoTodosAtendimentos = computed(() => authStore.hasPermission(PERMS.atendViewAll))

onMounted(async () => {
  if (!temPermissaoOperacional.value && temPermissaoExecutiva.value) {
    visaoExecutiva.value = true
  }

  const tarefas: Promise<unknown>[] = []
  if (temPermissaoOperacional.value) {
    tarefas.push(atendimentosStore.fetchAtendimentos(), crmStore.fetchCidadaos(1, 1))
  }
  await Promise.all(tarefas)

  if (temPermissaoExecutiva.value) {
    await analyticsStore.carregarDados({ executivo: true, territorial: false })
  }
})

// ==================== MÉTRICAS COMPUTADAS ====================

// 1. Atendimentos Abertos (não concluídos)
const atendimentosAbertos = computed(() => {
  return atendimentosStore.atendimentos.filter(a => a.status !== 'concluido').length
})

// 2. SLA em Atraso
const slaAtrasados = computed(() => {
  return atendimentosStore.atendimentosAtrasados.length
})

// 3. Base de Cidadãos
const totalCidadaos = computed(() => crmStore.cidadaosTotalCount)

// ==================== DADOS PARA COMPONENTES ====================

// Dados do gráfico de macrotemas
const dadosGrafico = computed(() => {
  return atendimentosStore.atendimentosPorMacrotema
})

// Últimos 5 atendimentos
const ultimosAtendimentos = computed(() => {
  return [...atendimentosStore.atendimentos]
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .slice(0, 5)
})

// ==================== LOADING STATE ====================

const carregando = computed(() => {
  if (!temPermissaoOperacional.value) {
    return false
  }
  return atendimentosStore.loading || crmStore.loading
})

// ==================== HELPERS PARA VISÃO EXECUTIVA ====================

function getIconeAtividade(tipo: string) {
  const icones: Record<string, any> = {
    ticket_transferido: ArrowRight,
    cidadao_criado: UserPlus,
    evento_criado: Calendar,
    documento_assinado: FileCheck,
    status_alterado: CheckCircle
  }
  return icones[tipo] || Activity
}

function formatarTempoRelativo(timestamp: string): string {
  const agora = Date.now()
  const diff = agora - new Date(timestamp).getTime()
  const minutos = Math.floor(diff / 60000)
  const horas = Math.floor(diff / 3600000)
  const dias = Math.floor(diff / 86400000)

  if (minutos < 60) return `${minutos} min atrás`
  if (horas < 24) return `${horas}h atrás`
  return `${dias}d atrás`
}

</script>

<template>
  <div class="space-y-6">
    <!-- Cabeçalho com Boas-vindas e Toggle de Visão -->
    <div class="card">
      <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center flex-shrink-0">
            <Sparkles class="w-6 h-6 text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <h2 class="text-2xl font-bold text-gray-900 dark:text-slate-100">
              Olá, {{ authStore.usuario?.nome }}! 👋
            </h2>
            <p class="text-gray-600 dark:text-slate-400 mt-1">
              Bem-vindo ao seu painel de gestão. Aqui está um resumo das suas atividades.
            </p>
            <p
              v-if="temPermissaoOperacional && !visaoExecutiva && !escopoTodosAtendimentos"
              class="text-xs text-amber-700 dark:text-amber-400 mt-1"
            >
              Métricas de atendimentos consideram apenas protocolos atribuídos a você.
            </p>
          </div>
        </div>

        <!-- Toggle de Visão (Apenas para Gestores) -->
        <div
          v-if="temPermissaoExecutiva && temPermissaoOperacional"
          class="flex items-center gap-3 px-4 py-2 bg-gray-50 dark:bg-slate-800 rounded-lg border border-gray-200 dark:border-slate-700"
        >
          <span 
            :class="[!visaoExecutiva ? 'text-gray-900 dark:text-slate-100 font-semibold' : 'text-gray-500 dark:text-slate-400']" 
            class="text-sm whitespace-nowrap"
          >
            Visão Operacional
          </span>
          <button
            @click="visaoExecutiva = !visaoExecutiva"
            :class="[visaoExecutiva ? 'bg-primary-600' : 'bg-gray-300 dark:bg-slate-600']"
            class="relative inline-flex h-7 w-14 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-slate-900"
            :title="visaoExecutiva ? 'Mudar para Visão Operacional' : 'Mudar para Visão Executiva'"
          >
            <span
              :class="[visaoExecutiva ? 'translate-x-8' : 'translate-x-1']"
              class="inline-block h-5 w-5 transform rounded-full bg-white transition-transform shadow-sm"
            />
          </button>
          <span 
            :class="[visaoExecutiva ? 'text-gray-900 dark:text-slate-100 font-semibold' : 'text-gray-500 dark:text-slate-400']" 
            class="text-sm whitespace-nowrap"
          >
            Visão Executiva
          </span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="carregando" class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div v-for="i in 3" :key="i" class="card animate-pulse">
        <div class="h-32 bg-gray-200 dark:bg-slate-700 rounded"></div>
      </div>
    </div>

    <!-- ==================== VISÃO OPERACIONAL ==================== -->
    <template v-else-if="!visaoExecutiva && temPermissaoOperacional">
      <!-- Cards de Métricas -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard
          label="Atendimentos Abertos"
          :valor="atendimentosAbertos"
          :icone="Inbox"
          cor="blue"
        />
        
        <MetricCard
          label="SLA em Atraso"
          :valor="slaAtrasados"
          :icone="AlertCircle"
          cor="red"
        />
        
        <MetricCard
          label="Base de Cidadãos"
          :valor="totalCidadaos"
          :icone="Users"
          cor="green"
        />
      </div>

      <!-- Área Central: Gráfico + Quick Actions -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Gráfico de Macrotemas (2 colunas) -->
        <div class="lg:col-span-2">
          <MacrotemaChart :dados="dadosGrafico" />
        </div>

        <!-- Quick Actions (1 coluna) -->
        <div class="lg:col-span-1">
          <QuickActions />
        </div>
      </div>

      <!-- Últimos Atendimentos -->
      <RecentAtendimentos :atendimentos="ultimosAtendimentos" />

      <!-- Top 5 Tags de Atendimento -->
      <div class="card">
        <div class="mb-4">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
            🔥 Assuntos Mais Recorrentes
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Top 5 tags de atendimento mais solicitadas
          </p>
        </div>

        <div v-if="atendimentosStore.topTagsAtendimento.length === 0" class="text-center py-8 text-gray-500 dark:text-slate-400">
          Nenhum dado disponível ainda
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="(item, index) in atendimentosStore.topTagsAtendimento"
            :key="item.tag.id"
            class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-slate-800 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors"
          >
            <!-- Ranking -->
            <div 
              :class="[
                index === 0 ? 'bg-yellow-500' : index === 1 ? 'bg-gray-400' : index === 2 ? 'bg-orange-600' : 'bg-gray-300 dark:bg-gray-600',
                'w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0'
              ]"
            >
              {{ index + 1 }}
            </div>

            <!-- Tag -->
            <div class="flex-1 min-w-0">
              <span
                :style="{
                  backgroundColor: item.tag.cor + '20',
                  color: item.tag.cor,
                  borderColor: item.tag.cor + '40'
                }"
                class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border"
              >
                {{ item.tag.nome }}
              </span>
            </div>

            <!-- Contagem -->
            <div class="flex items-center gap-2 flex-shrink-0">
              <span class="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {{ item.count }}
              </span>
              <span class="text-sm text-gray-500 dark:text-gray-400">
                {{ item.count === 1 ? 'atendimento' : 'atendimentos' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ==================== VISÃO EXECUTIVA ==================== -->
    <template v-else-if="visaoExecutiva && temPermissaoExecutiva">
      <!-- Métricas Executivas -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div class="card bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-blue-100 text-sm font-medium">Total Concluídos</p>
              <p class="text-3xl font-bold mt-2">{{ analyticsStore.totalConcluidos }}</p>
            </div>
            <div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
              <CheckCircle class="w-6 h-6" />
            </div>
          </div>
        </div>

        <div class="card bg-gradient-to-br from-red-500 to-red-600 text-white">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-red-100 text-sm font-medium">Total Atrasados</p>
              <p class="text-3xl font-bold mt-2">{{ analyticsStore.totalAtrasados }}</p>
            </div>
            <div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
              <Clock class="w-6 h-6" />
            </div>
          </div>
        </div>

        <div class="card bg-gradient-to-br from-green-500 to-green-600 text-white">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-green-100 text-sm font-medium">Equipe Ativa</p>
              <p class="text-3xl font-bold mt-2">{{ analyticsStore.produtividade.length }}</p>
            </div>
            <div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
              <Users class="w-6 h-6" />
            </div>
          </div>
        </div>

        <div class="card bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-purple-100 text-sm font-medium">Atividades (24h)</p>
              <p class="text-3xl font-bold mt-2">{{ analyticsStore.atividadesRecentes24h.length }}</p>
            </div>
            <div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
              <Activity class="w-6 h-6" />
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Ranking de Produtividade -->
        <div class="lg:col-span-2 card">
          <div class="mb-4 flex items-center justify-between">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                <TrendingUp class="w-5 h-5 text-primary-600 dark:text-primary-400" />
                Ranking de Produtividade
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Performance da equipe por taxa de conclusão
              </p>
            </div>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="border-b border-gray-200 dark:border-slate-700">
                  <th class="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">#</th>
                  <th class="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Assessor</th>
                  <th class="text-center py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Concluídos</th>
                  <th class="text-center py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Atrasados</th>
                  <th class="text-center py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Em Andamento</th>
                  <th class="text-right py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Taxa de Sucesso</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(assessor, index) in analyticsStore.topPerformers"
                  :key="assessor.userId"
                  class="border-b border-gray-100 dark:border-slate-800 hover:bg-gray-50 dark:hover:bg-slate-800/50 transition-colors"
                >
                  <td class="py-3 px-4">
                    <div
                      :class="[
                        index === 0 ? 'bg-yellow-500' : index === 1 ? 'bg-gray-400' : index === 2 ? 'bg-orange-600' : 'bg-gray-300 dark:bg-gray-600',
                        'w-7 h-7 rounded-full flex items-center justify-center text-white font-bold text-xs'
                      ]"
                    >
                      {{ index + 1 }}
                    </div>
                  </td>
                  <td class="py-3 px-4">
                    <span class="font-medium text-gray-900 dark:text-gray-100">{{ assessor.nomeUsuario }}</span>
                  </td>
                  <td class="py-3 px-4 text-center">
                    <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400">
                      {{ assessor.concluidos }}
                    </span>
                  </td>
                  <td class="py-3 px-4 text-center">
                    <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400">
                      {{ assessor.atrasados }}
                    </span>
                  </td>
                  <td class="py-3 px-4 text-center">
                    <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400">
                      {{ assessor.emAndamento }}
                    </span>
                  </td>
                  <td class="py-3 px-4 text-right">
                    <div class="flex items-center justify-end gap-2">
                      <div class="w-20 bg-gray-200 dark:bg-slate-700 rounded-full h-2">
                        <div
                          :class="[
                            assessor.taxaSucesso >= 80 ? 'bg-green-500' : assessor.taxaSucesso >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                          ]"
                          class="h-2 rounded-full transition-all"
                          :style="{ width: assessor.taxaSucesso + '%' }"
                        ></div>
                      </div>
                      <span class="font-semibold text-gray-900 dark:text-gray-100 w-12 text-right">
                        {{ assessor.taxaSucesso.toFixed(0) }}%
                      </span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Gargalos (Gráfico de Rosca) -->
        <div class="card">
          <div class="mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
              <AlertTriangle class="w-5 h-5 text-red-600 dark:text-red-400" />
              Gargalos
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Atendimentos atrasados por área
            </p>
          </div>

          <!-- Gráfico de Rosca (CSS Puro) -->
          <div class="flex items-center justify-center mb-6">
            <div class="relative w-48 h-48">
              <svg viewBox="0 0 100 100" class="transform -rotate-90">
                <!-- Anel externo -->
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  fill="none"
                  stroke="#e5e7eb"
                  stroke-width="10"
                  class="dark:stroke-slate-700"
                />
                
                <!-- Segmentos -->
                <circle
                  v-for="(item, index) in analyticsStore.gargalos"
                  :key="item.macrotema"
                  cx="50"
                  cy="50"
                  r="40"
                  fill="none"
                  :stroke="item.cor"
                  stroke-width="10"
                  :stroke-dasharray="`${(item.atrasados / Math.max(analyticsStore.totalAtrasados, 1) * 251.2).toFixed(1)} 251.2`"
                  :stroke-dashoffset="251.2 - analyticsStore.gargalos.slice(0, index).reduce((sum, g) => sum + (g.atrasados / Math.max(analyticsStore.totalAtrasados, 1) * 251.2), 0)"
                  class="transition-all"
                />
              </svg>
              
              <!-- Centro do gráfico -->
              <div class="absolute inset-0 flex items-center justify-center flex-col">
                <span class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ analyticsStore.totalAtrasados }}</span>
                <span class="text-xs text-gray-600 dark:text-gray-400">Atrasados</span>
              </div>
            </div>
          </div>

          <!-- Legenda -->
          <div class="space-y-2">
            <div
              v-for="item in analyticsStore.gargalos"
              :key="item.macrotema"
              class="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-800 transition-colors"
            >
              <div class="flex items-center gap-2">
                <div
                  class="w-3 h-3 rounded-full flex-shrink-0"
                  :style="{ backgroundColor: item.cor }"
                ></div>
                <span class="text-sm text-gray-700 dark:text-gray-300">{{ item.macrotema }}</span>
              </div>
              <span class="text-sm font-semibold text-gray-900 dark:text-gray-100">{{ item.atrasados }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Auditoria de Ações (Activity Feed) -->
      <div class="card">
        <div class="mb-4">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <Activity class="w-5 h-5 text-primary-600 dark:text-primary-400" />
            Auditoria de Ações
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Timeline de atividades recentes da equipe
          </p>
        </div>

        <div class="space-y-4 relative before:absolute before:left-6 before:top-0 before:bottom-0 before:w-px before:bg-gray-200 dark:before:bg-slate-700">
          <div
            v-for="atividade in analyticsStore.atividadesRecentes"
            :key="atividade.id"
            class="relative flex items-start gap-4 pl-2"
          >
            <!-- Ícone -->
            <div
              :style="{ backgroundColor: atividade.cor }"
              class="relative z-10 w-10 h-10 rounded-full flex items-center justify-center text-white flex-shrink-0"
            >
              <component :is="getIconeAtividade(atividade.tipo)" class="w-5 h-5" />
            </div>

            <!-- Conteúdo -->
            <div class="flex-1 bg-gray-50 dark:bg-slate-800 rounded-lg p-4">
              <div class="flex items-start justify-between gap-4">
                <div>
                  <p class="text-sm text-gray-900 dark:text-gray-100">
                    <span class="font-semibold">{{ atividade.usuario }}</span>
                    <span class="text-gray-600 dark:text-gray-400 ml-1">{{ atividade.descricao }}</span>
                  </p>
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {{ formatarTempoRelativo(atividade.timestamp) }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <div
      v-else
      class="card text-center py-12 text-gray-500 dark:text-slate-400"
    >
      Nenhuma visão do dashboard está disponível para o seu perfil.
    </div>
  </div>
</template>
