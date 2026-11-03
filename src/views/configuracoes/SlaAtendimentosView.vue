<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAtendimentosStore } from '@/stores/atendimentos'
import { PERMS } from '@/constants/rbac'
import Button from '@/components/common/Button.vue'
import { Clock, CalendarDays, Save, Info } from 'lucide-vue-next'

const HORAS_POR_DIA = 24

const authStore = useAuthStore()
const atendimentosStore = useAtendimentosStore()

const loading = ref(true)
const salvando = ref(false)
const mensagem = ref<string | null>(null)
const unidade = ref<'dias' | 'horas'>('dias')

/** Valores exibidos no formulário (na unidade selecionada). */
const prazos = ref({
  baixa: 5,
  media: 3,
  alta: 2,
  urgente: 1,
})

const podeEditar = computed(() => authStore.hasPermission(PERMS.manageSlaAtend))

const prioridades = [
  {
    key: 'baixa' as const,
    label: 'Baixa',
    descricao: 'Demandas rotineiras, sem urgência imediata',
    cor: '#16a34a',
    bg: 'bg-green-50 dark:bg-green-950/30 border-green-200 dark:border-green-900/50',
  },
  {
    key: 'media' as const,
    label: 'Média',
    descricao: 'Prazo padrão da maioria dos protocolos',
    cor: '#2563eb',
    bg: 'bg-blue-50 dark:bg-blue-950/30 border-blue-200 dark:border-blue-900/50',
  },
  {
    key: 'alta' as const,
    label: 'Alta',
    descricao: 'Requer resposta prioritária da equipe',
    cor: '#ea580c',
    bg: 'bg-orange-50 dark:bg-orange-950/30 border-orange-200 dark:border-orange-900/50',
  },
  {
    key: 'urgente' as const,
    label: 'Urgente',
    descricao: 'Situações críticas ou com risco imediato',
    cor: '#dc2626',
    bg: 'bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-900/50',
  },
]

function horasFromApi(config: {
  horas_baixa: number
  horas_media: number
  horas_alta: number
  horas_urgente: number
}) {
  return {
    baixa: config.horas_baixa,
    media: config.horas_media,
    alta: config.horas_alta,
    urgente: config.horas_urgente,
  }
}

function aplicarHorasNoForm(horas: typeof prazos.value) {
  if (unidade.value === 'dias') {
    prazos.value = {
      baixa: horas.baixa / HORAS_POR_DIA,
      media: horas.media / HORAS_POR_DIA,
      alta: horas.alta / HORAS_POR_DIA,
      urgente: horas.urgente / HORAS_POR_DIA,
    }
  } else {
    prazos.value = { ...horas }
  }
}

/** Horas armazenadas no banco a partir dos valores exibidos. */
function horasParaSalvar() {
  const round = (n: number) => Math.max(1, Math.min(8760, Math.round(n)))
  if (unidade.value === 'dias') {
    return {
      horas_baixa: round(prazos.value.baixa * HORAS_POR_DIA),
      horas_media: round(prazos.value.media * HORAS_POR_DIA),
      horas_alta: round(prazos.value.alta * HORAS_POR_DIA),
      horas_urgente: round(prazos.value.urgente * HORAS_POR_DIA),
    }
  }
  return {
    horas_baixa: round(prazos.value.baixa),
    horas_media: round(prazos.value.media),
    horas_alta: round(prazos.value.alta),
    horas_urgente: round(prazos.value.urgente),
  }
}

function equivalenteHoras(key: keyof typeof prazos.value): number {
  const v = prazos.value[key]
  return unidade.value === 'dias' ? Math.round(v * HORAS_POR_DIA) : Math.round(v)
}

function equivalenteDias(key: keyof typeof prazos.value): string {
  const horas =
    unidade.value === 'dias' ? prazos.value[key] * HORAS_POR_DIA : prazos.value[key]
  const dias = horas / HORAS_POR_DIA
  if (dias >= 1 && Math.abs(dias - Math.round(dias)) < 0.01) {
    return `${Math.round(dias)} dia${Math.round(dias) === 1 ? '' : 's'}`
  }
  return `${dias.toLocaleString('pt-BR', { maximumFractionDigits: 1 })} dias`
}

let horasCache: typeof prazos.value | null = null

watch(unidade, (nova, antiga) => {
  if (!horasCache) return
  if (nova === antiga) return
  if (nova === 'dias') {
    prazos.value = {
      baixa: horasCache.baixa / HORAS_POR_DIA,
      media: horasCache.media / HORAS_POR_DIA,
      alta: horasCache.alta / HORAS_POR_DIA,
      urgente: horasCache.urgente / HORAS_POR_DIA,
    }
  } else {
    prazos.value = { ...horasCache }
  }
})

watch(
  prazos,
  () => {
    horasCache = horasParaSalvar()
    horasCache = {
      baixa: horasCache.horas_baixa,
      media: horasCache.horas_media,
      alta: horasCache.horas_alta,
      urgente: horasCache.horas_urgente,
    }
  },
  { deep: true },
)

onMounted(async () => {
  try {
    const config = await atendimentosStore.fetchConfiguracaoSla()
    const h = horasFromApi(config)
    horasCache = h
    aplicarHorasNoForm(h)
  } finally {
    loading.value = false
  }
})

const salvar = async () => {
  if (!podeEditar.value) return
  salvando.value = true
  mensagem.value = null
  try {
    const horas = horasParaSalvar()
    if (unidade.value === 'dias') {
      await atendimentosStore.updateConfiguracaoSla({
        dias_baixa: prazos.value.baixa,
        dias_media: prazos.value.media,
        dias_alta: prazos.value.alta,
        dias_urgente: prazos.value.urgente,
      })
    } else {
      await atendimentosStore.updateConfiguracaoSla(horas)
    }
    horasCache = {
      baixa: horas.horas_baixa,
      media: horas.horas_media,
      alta: horas.horas_alta,
      urgente: horas.horas_urgente,
    }
    mensagem.value =
      'Prazos atualizados. O sistema grava o equivalente em horas; atendimentos já abertos mantêm o vencimento até mudança de prioridade.'
  } catch {
    mensagem.value = 'Erro ao salvar. Verifique os valores e tente novamente.'
  } finally {
    salvando.value = false
  }
}

const inputStep = computed(() => (unidade.value === 'dias' ? 0.5 : 1))
const inputMin = computed(() => (unidade.value === 'dias' ? 0.5 : 1))
const inputMax = computed(() => (unidade.value === 'dias' ? 365 : 8760))
</script>

<template>
  <div v-if="loading" class="text-gray-500 dark:text-slate-400 py-8">Carregando…</div>

  <div v-else class="space-y-6 max-w-2xl">
    <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
      <div class="space-y-2">
        <p class="text-sm text-gray-600 dark:text-slate-400 leading-relaxed">
          Prazo corrido a partir da abertura do protocolo, por prioridade. No banco o sistema
          <strong>sempre armazena horas</strong>; ao informar dias, a conversão é automática
          (1 dia = 24 h).
        </p>
        <p class="text-xs text-gray-500 dark:text-slate-500 flex items-start gap-1.5">
          <Info class="w-3.5 h-3.5 shrink-0 mt-0.5" />
          Também editável no Django Admin em «Configuração de SLA».
        </p>
      </div>

      <div
        class="inline-flex rounded-lg border border-gray-200 dark:border-slate-700 p-0.5 bg-gray-50 dark:bg-slate-900 shrink-0"
        role="group"
        aria-label="Unidade de prazo"
      >
        <button
          type="button"
          :class="[
            unidade === 'dias'
              ? 'bg-white dark:bg-slate-800 shadow-sm text-gray-900 dark:text-slate-100'
              : 'text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-slate-200',
            'flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors',
          ]"
          :disabled="salvando"
          @click="unidade = 'dias'"
        >
          <CalendarDays class="w-4 h-4" />
          Dias
        </button>
        <button
          type="button"
          :class="[
            unidade === 'horas'
              ? 'bg-white dark:bg-slate-800 shadow-sm text-gray-900 dark:text-slate-100'
              : 'text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-slate-200',
            'flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors',
          ]"
          :disabled="salvando"
          @click="unidade = 'horas'"
        >
          <Clock class="w-4 h-4" />
          Horas
        </button>
      </div>
    </div>

    <div class="space-y-3">
      <article
        v-for="item in prioridades"
        :key="item.key"
        :class="['rounded-xl border p-4 transition-shadow', item.bg]"
      >
        <div class="flex flex-col sm:flex-row sm:items-center gap-4">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span
                class="w-2.5 h-2.5 rounded-full shrink-0"
                :style="{ backgroundColor: item.cor }"
              />
              <h3 class="font-semibold text-gray-900 dark:text-slate-100">{{ item.label }}</h3>
            </div>
            <p class="text-xs text-gray-600 dark:text-slate-400 mt-1">{{ item.descricao }}</p>
            <p class="text-xs text-gray-500 dark:text-slate-500 mt-2 tabular-nums">
              <template v-if="unidade === 'dias'">
                ≈ {{ equivalenteHoras(item.key) }} h no sistema
                <span class="text-gray-400 dark:text-slate-600"> · </span>
                {{ equivalenteDias(item.key) }} corridos
              </template>
              <template v-else>
                ≈ {{ equivalenteDias(item.key) }} corridos
              </template>
            </p>
          </div>

          <div class="flex items-center gap-2 sm:justify-end">
            <input
              v-model.number="prazos[item.key]"
              type="number"
              :step="inputStep"
              :min="inputMin"
              :max="inputMax"
              class="input w-24 text-right text-lg font-semibold tabular-nums"
              :disabled="!podeEditar || salvando"
              :aria-label="`Prazo prioridade ${item.label}`"
            />
            <span class="text-sm font-medium text-gray-600 dark:text-slate-400 w-12">
              {{ unidade === 'dias' ? (prazos[item.key] === 1 ? 'dia' : 'dias') : 'horas' }}
            </span>
          </div>
        </div>
      </article>
    </div>

    <p v-if="!podeEditar" class="text-sm text-amber-700 dark:text-amber-400">
      Visualização apenas. Para alterar, é necessária a permissão «SLA de Atendimentos».
    </p>

    <p
      v-if="mensagem"
      class="text-sm text-gray-700 dark:text-slate-300 p-3 rounded-lg bg-gray-50 dark:bg-slate-900 border border-gray-100 dark:border-slate-800"
    >
      {{ mensagem }}
    </p>

    <Button v-if="podeEditar" variant="primary" :loading="salvando" @click="salvar">
      <Save class="w-4 h-4" />
      Salvar prazos
    </Button>
  </div>
</template>
