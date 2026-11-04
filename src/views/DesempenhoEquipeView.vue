<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAnalyticsStore } from '@/stores/analytics'
import { useAlertDialog } from '@/composables/useAlertDialog'
import MacrotemaChart from '@/components/dashboard/MacrotemaChart.vue'
import MetricCard from '@/components/dashboard/MetricCard.vue'
import {
  Users,
  Search,
  CalendarRange,
  TrendingUp,
  TrendingDown,
  Minus,
  Activity,
  CheckCircle,
  Clock,
  AlertCircle,
  Inbox,
  ChevronRight,
  BarChart3,
  Download,
} from 'lucide-vue-next'

const { showSuccess, showError } = useAlertDialog()

type PeriodoPreset = '7d' | '30d' | '90d' | 'tudo'

const route = useRoute()
const router = useRouter()
const analyticsStore = useAnalyticsStore()

const buscaMembro = ref('')
const assessorSelecionadoId = ref('')
const presetPeriodo = ref<PeriodoPreset>('30d')
const dataDe = ref('')
const dataAte = ref('')
const exportandoCsv = ref(false)

const membrosFiltrados = computed(() => {
  const q = buscaMembro.value.trim().toLowerCase()
  if (!q) return analyticsStore.equipeMembros
  return analyticsStore.equipeMembros.filter(
    m =>
      m.nome.toLowerCase().includes(q) ||
      m.email.toLowerCase().includes(q) ||
      m.cargo.toLowerCase().includes(q),
  )
})

const detalhe = computed(() => analyticsStore.assessorDetalhe)

const periodoQuery = computed(() => {
  if (presetPeriodo.value === 'tudo') {
    return { de: undefined as string | undefined, ate: undefined as string | undefined }
  }
  const ate = new Date()
  const de = new Date()
  const dias = presetPeriodo.value === '7d' ? 7 : presetPeriodo.value === '90d' ? 90 : 30
  de.setDate(de.getDate() - dias)
  const fmt = (d: Date) => d.toISOString().slice(0, 10)
  return { de: fmt(de), ate: fmt(ate) }
})

const dadosMacrotema = computed(() =>
  (detalhe.value?.porMacrotema ?? []).map(m => ({
    macrotema: m.macrotema,
    cor: m.cor,
    quantidade: m.quantidade,
  })),
)

function aplicarPreset(p: PeriodoPreset) {
  presetPeriodo.value = p
  dataDe.value = ''
  dataAte.value = ''
}

function periodoEfetivo() {
  if (dataDe.value || dataAte.value) {
    return { de: dataDe.value || undefined, ate: dataAte.value || undefined }
  }
  return periodoQuery.value
}

async function carregarDetalhe() {
  if (!assessorSelecionadoId.value) return
  const p = periodoEfetivo()
  await analyticsStore.carregarAssessorDesempenho({
    responsavelId: assessorSelecionadoId.value,
    de: p.de,
    ate: p.ate,
  })
}

function baixarBlob(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  window.URL.revokeObjectURL(url)
}

async function exportarEquipeCsv() {
  exportandoCsv.value = true
  try {
    const blob = await analyticsStore.exportEquipeDesempenhoCsv()
    baixarBlob(blob, `desempenho-equipe-${new Date().toISOString().slice(0, 10)}.csv`)
    showSuccess('CSV da equipe gerado com sucesso.')
  } catch {
    showError('Não foi possível exportar o CSV da equipe.')
  } finally {
    exportandoCsv.value = false
  }
}

async function exportarAssessorCsv() {
  if (!assessorSelecionadoId.value) return
  exportandoCsv.value = true
  try {
    const p = periodoEfetivo()
    const blob = await analyticsStore.exportAssessorDesempenhoCsv({
      responsavelId: assessorSelecionadoId.value,
      de: p.de,
      ate: p.ate,
    })
    const slug =
      detalhe.value?.assessor.nome
        .toLowerCase()
        .replace(/[^\w]+/g, '-')
        .replace(/-+/g, '-')
        .slice(0, 40) || 'assessor'
    baixarBlob(blob, `desempenho-${slug}-${new Date().toISOString().slice(0, 10)}.csv`)
    showSuccess('Relatório CSV do assessor gerado com sucesso.')
  } catch {
    showError('Não foi possível exportar o CSV do assessor.')
  } finally {
    exportandoCsv.value = false
  }
}

function selecionarMembro(userId: string) {
  assessorSelecionadoId.value = userId
  router.replace({ query: { ...route.query, assessor: userId } })
}

function formatarRelativo(iso: string) {
  const diff = Date.now() - new Date(iso).getTime()
  const min = Math.floor(diff / 60000)
  const h = Math.floor(diff / 3600000)
  const d = Math.floor(diff / 86400000)
  if (min < 60) return `${min} min atrás`
  if (h < 24) return `${h}h atrás`
  return `${d}d atrás`
}

const deltaIcon = computed(() => {
  const d = detalhe.value?.comparativoEquipe.deltaTaxa ?? 0
  if (d > 0.5) return TrendingUp
  if (d < -0.5) return TrendingDown
  return Minus
})

onMounted(async () => {
  await analyticsStore.carregarEquipeDesempenho()
  const fromQuery = route.query.assessor as string | undefined
  const inicial =
    fromQuery && analyticsStore.equipeMembros.some(m => m.userId === fromQuery)
      ? fromQuery
      : analyticsStore.equipeMembros[0]?.userId ?? ''
  if (inicial) {
    assessorSelecionadoId.value = inicial
    await carregarDetalhe()
  }
})

watch([assessorSelecionadoId, presetPeriodo, dataDe, dataAte], () => {
  carregarDetalhe()
})

watch(assessorSelecionadoId, id => {
  if (id) router.replace({ query: { ...route.query, assessor: id } })
})
</script>

<template>
  <div class="space-y-6">
    <!-- Cabeçalho -->
    <div class="card">
      <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-slate-100 flex items-center gap-2">
            <BarChart3 class="w-7 h-7 text-primary-600 dark:text-primary-400" />
            Desempenho da Equipe
          </h1>
          <p class="text-gray-600 dark:text-slate-400 mt-1 max-w-2xl">
            Análise individual por assessor — complementa a visão executiva do dashboard com filtros
            por membro e período.
          </p>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <button
            type="button"
            class="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-lg border border-gray-300 dark:border-slate-600 hover:bg-gray-50 dark:hover:bg-slate-800 disabled:opacity-50"
            :disabled="exportandoCsv"
            @click="exportarEquipeCsv"
          >
            <Download class="w-4 h-4" />
            CSV equipe
          </button>
          <router-link
            to="/dashboard"
            class="text-sm font-medium text-primary-600 dark:text-primary-400 hover:underline inline-flex items-center gap-1 px-2 py-2"
          >
            Voltar ao dashboard
            <ChevronRight class="w-4 h-4" />
          </router-link>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-12 gap-6">
      <!-- Coluna: seleção de membro -->
      <div class="xl:col-span-4 space-y-4">
        <div class="card">
          <h2 class="text-sm font-semibold text-gray-900 dark:text-slate-100 uppercase tracking-wide mb-3">
            Membros da equipe
          </h2>
          <div class="relative mb-3">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              v-model="buscaMembro"
              type="search"
              placeholder="Buscar por nome ou e-mail…"
              class="w-full pl-9 pr-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-800"
            />
          </div>
          <div class="space-y-2 max-h-[420px] overflow-y-auto pr-1">
            <button
              v-for="membro in membrosFiltrados"
              :key="membro.userId"
              type="button"
              class="w-full text-left p-3 rounded-lg border-2 transition-all flex items-center gap-3"
              :class="
                assessorSelecionadoId === membro.userId
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  : 'border-gray-200 dark:border-slate-700 hover:border-primary-300 dark:hover:border-primary-700'
              "
              @click="selecionarMembro(membro.userId)"
            >
              <div
                class="w-10 h-10 rounded-full bg-primary-100 dark:bg-primary-900/40 flex items-center justify-center text-primary-700 dark:text-primary-300 font-bold text-sm flex-shrink-0"
              >
                {{ membro.nome.charAt(0).toUpperCase() }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-medium text-gray-900 dark:text-slate-100 truncate">{{ membro.nome }}</p>
                <p class="text-xs text-gray-500 dark:text-slate-400 truncate">{{ membro.cargo || membro.email }}</p>
              </div>
              <div class="text-right flex-shrink-0">
                <p class="text-sm font-bold text-gray-900 dark:text-slate-100">{{ membro.taxaSucesso.toFixed(0) }}%</p>
                <p class="text-xs text-gray-500">{{ membro.totalAtendimentos }} prot.</p>
              </div>
            </button>
            <p v-if="membrosFiltrados.length === 0" class="text-sm text-gray-500 py-6 text-center">
              Nenhum membro encontrado.
            </p>
          </div>
        </div>

        <!-- Período -->
        <div class="card">
          <h2 class="text-sm font-semibold text-gray-900 dark:text-slate-100 uppercase tracking-wide mb-3 flex items-center gap-2">
            <CalendarRange class="w-4 h-4" />
            Período de análise
          </h2>
          <div class="flex flex-wrap gap-2 mb-4">
            <button
              v-for="p in (['7d', '30d', '90d', 'tudo'] as PeriodoPreset[])"
              :key="p"
              type="button"
              class="px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors"
              :class="
                presetPeriodo === p
                  ? 'bg-primary-600 text-white border-primary-600'
                  : 'border-gray-300 dark:border-slate-600 text-gray-700 dark:text-slate-300'
              "
              @click="aplicarPreset(p)"
            >
              {{ p === '7d' ? '7 dias' : p === '30d' ? '30 dias' : p === '90d' ? '90 dias' : 'Tudo' }}
            </button>
          </div>
          <div class="grid grid-cols-2 gap-2 text-sm">
            <label class="block">
              <span class="text-xs text-gray-500">De</span>
              <input
                v-model="dataDe"
                type="date"
                class="mt-1 w-full rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-2 py-1.5"
                @change="presetPeriodo = 'tudo'"
              />
            </label>
            <label class="block">
              <span class="text-xs text-gray-500">Até</span>
              <input
                v-model="dataAte"
                type="date"
                class="mt-1 w-full rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-2 py-1.5"
                @change="presetPeriodo = 'tudo'"
              />
            </label>
          </div>
        </div>
      </div>

      <!-- Coluna: detalhe -->
      <div class="xl:col-span-8 space-y-6">
        <div v-if="!assessorSelecionadoId" class="card py-16 text-center text-gray-500">
          <Users class="w-12 h-12 mx-auto mb-3 opacity-40" />
          Selecione um assessor para ver o relatório individual.
        </div>

        <div v-else-if="analyticsStore.desempenhoLoading && !detalhe" class="card animate-pulse h-64" />

        <template v-else-if="detalhe">
          <!-- Perfil + comparativo -->
          <div class="card bg-gradient-to-br from-slate-50 to-white dark:from-slate-800 dark:to-slate-900">
            <div class="flex flex-col sm:flex-row sm:items-center gap-4 justify-between">
              <div class="flex items-center gap-4">
                <div
                  class="w-14 h-14 rounded-full bg-primary-600 text-white flex items-center justify-center text-xl font-bold"
                >
                  {{ detalhe.assessor.nome.charAt(0).toUpperCase() }}
                </div>
                <div>
                  <h2 class="text-xl font-bold text-gray-900 dark:text-slate-100">{{ detalhe.assessor.nome }}</h2>
                  <p class="text-sm text-gray-600 dark:text-slate-400">{{ detalhe.assessor.cargo }} · {{ detalhe.assessor.email }}</p>
                </div>
              </div>
              <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
                <div
                  class="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800"
                >
                  <component :is="deltaIcon" class="w-5 h-5 text-primary-600" />
                  <div>
                    <p class="text-xs text-gray-500">vs. média da equipe</p>
                    <p class="font-semibold text-gray-900 dark:text-slate-100">
                      {{ detalhe.comparativoEquipe.deltaTaxa > 0 ? '+' : '' }}{{ detalhe.comparativoEquipe.deltaTaxa.toFixed(1) }} pp
                      <span class="text-sm font-normal text-gray-500">
                        (média {{ detalhe.comparativoEquipe.taxaSucessoMedia.toFixed(1) }}%)
                      </span>
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  class="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium disabled:opacity-50"
                  :disabled="exportandoCsv"
                  @click="exportarAssessorCsv"
                >
                  <Download class="w-4 h-4" />
                  Exportar CSV
                </button>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard label="Total no período" :valor="detalhe.resumo.total" :icone="Inbox" cor="blue" />
            <MetricCard label="Concluídos" :valor="detalhe.resumo.concluidos" :icone="CheckCircle" cor="green" />
            <MetricCard label="SLA em atraso" :valor="detalhe.resumo.atrasados" :icone="AlertCircle" cor="red" />
            <MetricCard
              label="Taxa de conclusão"
              :valor="`${detalhe.resumo.taxaSucesso.toFixed(1)}%`"
              :icone="TrendingUp"
              cor="purple"
            />
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <MacrotemaChart :dados="dadosMacrotema" />

            <div class="card">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-slate-100 mb-4">Por status</h3>
              <div class="space-y-3">
                <div
                  v-for="item in detalhe.porStatus"
                  :key="item.status"
                  class="flex items-center justify-between gap-2"
                >
                  <span class="text-sm text-gray-700 dark:text-slate-300">{{ item.rotulo }}</span>
                  <span class="font-semibold text-gray-900 dark:text-slate-100">{{ item.quantidade }}</span>
                </div>
                <p v-if="detalhe.porStatus.length === 0" class="text-sm text-gray-500">Sem atendimentos no período.</p>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="card">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-slate-100 mb-4 flex items-center gap-2">
                <Clock class="w-5 h-5" />
                Protocolos recentes
              </h3>
              <div class="overflow-x-auto">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="border-b border-gray-200 dark:border-slate-700 text-left text-gray-500">
                      <th class="py-2 pr-2">Protocolo</th>
                      <th class="py-2 pr-2">Cidadão</th>
                      <th class="py-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="att in detalhe.atendimentosRecentes"
                      :key="att.id"
                      class="border-b border-gray-100 dark:border-slate-800"
                    >
                      <td class="py-2.5 pr-2 font-medium">
                        <router-link
                          :to="`/atendimentos/${att.id}`"
                          class="text-primary-600 hover:underline"
                        >
                          #{{ att.protocolo }}
                        </router-link>
                        <span
                          v-if="att.atrasado"
                          class="ml-1 text-xs text-red-600 dark:text-red-400"
                        >SLA</span>
                      </td>
                      <td class="py-2.5 pr-2 text-gray-600 dark:text-slate-400 truncate max-w-[120px]">
                        {{ att.cidadaoNome }}
                      </td>
                      <td class="py-2.5">
                        <span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-slate-700">
                          {{ att.statusRotulo }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <p v-if="detalhe.atendimentosRecentes.length === 0" class="text-sm text-gray-500 py-4">
                  Nenhum protocolo no período.
                </p>
              </div>
            </div>

            <div class="card">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-slate-100 mb-4 flex items-center gap-2">
                <Activity class="w-5 h-5" />
                Atividade do assessor
              </h3>
              <div class="space-y-3 max-h-80 overflow-y-auto">
                <div
                  v-for="ev in detalhe.atividades"
                  :key="ev.id"
                  class="p-3 rounded-lg bg-gray-50 dark:bg-slate-800/80 text-sm"
                >
                  <p class="text-gray-900 dark:text-slate-100">{{ ev.descricao }}</p>
                  <p class="text-xs text-gray-500 mt-1">{{ formatarRelativo(ev.timestamp) }}</p>
                </div>
                <p v-if="detalhe.atividades.length === 0" class="text-sm text-gray-500">
                  Sem movimentações registradas no período.
                </p>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
