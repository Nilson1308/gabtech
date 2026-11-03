<script setup lang="ts">
import { computed, ref } from 'vue'
import { useFormatters } from '@/composables/useFormatters'
import type { AuditoriaAlvo } from '@/services/auditoria'
import type { Rastreabilidade } from '@/utils/rastreabilidade'
import { rotuloUltimaAcao } from '@/utils/rastreabilidade'
import HistoricoAuditoriaModal from '@/components/common/HistoricoAuditoriaModal.vue'

const props = withDefaults(
  defineProps<{
    rastreabilidade?: Rastreabilidade | null
    compact?: boolean
    showCriacao?: boolean
    alvoAuditoria?: AuditoriaAlvo | null
    historicoTitulo?: string
  }>(),
  {
    rastreabilidade: null,
    compact: false,
    showCriacao: false,
    alvoAuditoria: null,
    historicoTitulo: '',
  },
)

const { formatDate } = useFormatters()
const historicoAberto = ref(false)

const linhaPrincipal = computed(() => {
  const r = props.rastreabilidade
  if (!r?.ultimaAcaoEm && !r?.criadoEm) return null
  const quando = r.ultimaAcaoEm || r.criadoEm
  const quem = r.ultimaAcaoPorNome || r.criadoPorNome
  const rotulo = rotuloUltimaAcao(r.ultimaAcaoTipo)
  if (!quando) return null
  const dataHora = formatDate(quando, true)
  if (quem) {
    return `${rotulo}: ${dataHora} · ${quem}`
  }
  return `${rotulo}: ${dataHora}`
})

const linhaCriacao = computed(() => {
  if (!props.showCriacao || !props.rastreabilidade?.criadoEm) return null
  const r = props.rastreabilidade
  const dataHora = formatDate(r.criadoEm!, true)
  if (r.criadoPorNome) {
    return `Cadastro: ${dataHora} · ${r.criadoPorNome}`
  }
  return `Cadastro: ${dataHora}`
})

const mostrarHistorico = computed(() => Boolean(props.alvoAuditoria?.objectId))

const temConteudo = computed(
  () => Boolean(linhaPrincipal.value || linhaCriacao.value || mostrarHistorico.value),
)
</script>

<template>
  <div v-if="temConteudo" class="space-y-0.5">
    <p
      v-if="linhaPrincipal"
      class="text-gray-500 dark:text-slate-400"
      :class="compact ? 'text-[11px] leading-tight' : 'text-xs'"
    >
      {{ linhaPrincipal }}
    </p>
    <p
      v-if="linhaCriacao && showCriacao"
      class="text-gray-500 dark:text-slate-400 text-[11px] leading-tight"
    >
      {{ linhaCriacao }}
    </p>
    <button
      v-if="mostrarHistorico"
      type="button"
      class="text-[11px] text-primary-600 dark:text-primary-400 hover:underline"
      @click="historicoAberto = true"
    >
      Ver histórico completo
    </button>
    <HistoricoAuditoriaModal
      :open="historicoAberto"
      :alvo="alvoAuditoria"
      :titulo="historicoTitulo || 'Histórico de ações'"
      @close="historicoAberto = false"
    />
  </div>
</template>
