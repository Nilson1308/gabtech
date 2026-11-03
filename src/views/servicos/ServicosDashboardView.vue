<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useServicosStore } from '@/stores/servicos'
import { useAuthStore } from '@/stores/auth'
import { hasGerenciamentoServicos, PERMS } from '@/constants/rbac'
import {
  ArrowRight,
  Briefcase,
  Gift,
  GraduationCap,
  Loader2,
  Sparkles,
  Users,
} from 'lucide-vue-next'

const servicosStore = useServicosStore()
const authStore = useAuthStore()
const router = useRouter()
const carregando = ref(true)

const podeGerenciar = computed(() =>
  hasGerenciamentoServicos(authStore.usuario?.permissions ?? []),
)

const vagasAbertas = computed(
  () => servicosStore.vagas.filter(v => v.status === 'aberta').length,
)
const totalCandidaturas = computed(() => servicosStore.candidaturas.length)
const totalItensBeneficio = computed(() => servicosStore.itensBeneficio.length)
const entregasRecentes = computed(() => servicosStore.entregasBeneficio.length)
const turmasAbertas = computed(
  () => servicosStore.turmas.filter(t => t.status === 'aberta').length,
)
const inscricoesAtivas = computed(() =>
  servicosStore.inscricoes.filter(i => i.status !== 'cancelado').length,
)

const secoes = computed(() => [
  {
    id: 'talentos',
    titulo: 'Banco de Talentos',
    descricao: 'Vagas, pipeline seletivo e vínculo de candidatos com currículo no CRM.',
    rota: '/servicos/talentos',
    icone: Briefcase,
    cor: '#6366f1',
    metricas: [
      { label: 'Vagas abertas', valor: vagasAbertas.value },
      { label: 'Candidaturas', valor: totalCandidaturas.value },
    ],
  },
  {
    id: 'beneficios',
    titulo: 'Assistência Social',
    descricao: 'Itens de benefício, entregas e público sugerido por tags.',
    rota: '/servicos/beneficios',
    icone: Gift,
    cor: '#059669',
    metricas: [
      { label: 'Itens cadastrados', valor: totalItensBeneficio.value },
      { label: 'Entregas registradas', valor: entregasRecentes.value },
    ],
  },
  {
    id: 'cursos',
    titulo: 'Cursos & Capacitação',
    descricao: 'Turmas, vagas, inscrições e lista de espera automática.',
    rota: '/servicos/cursos',
    icone: GraduationCap,
    cor: '#7c3aed',
    metricas: [
      { label: 'Turmas abertas', valor: turmasAbertas.value },
      { label: 'Inscrições ativas', valor: inscricoesAtivas.value },
    ],
  },
])

onMounted(async () => {
  carregando.value = true
  try {
    await servicosStore.carregarResumoModulo()
  } finally {
    carregando.value = false
  }
})

function ir(rota: string) {
  router.push(rota)
}
</script>

<template>
  <div class="space-y-6">
    <div
      class="rounded-xl border border-indigo-200 dark:border-indigo-900/50 bg-gradient-to-br from-indigo-50 to-white dark:from-indigo-950/40 dark:to-slate-900 p-5 flex flex-col sm:flex-row sm:items-center gap-4"
    >
      <div class="flex items-start gap-3 flex-1">
        <div class="p-2 rounded-lg bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300">
          <Sparkles class="w-6 h-6" />
        </div>
        <div>
          <h2 class="text-lg font-semibold text-gray-900 dark:text-slate-100">Matchmaking por tags</h2>
          <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
            Vagas e turmas usam tags de <strong>contexto profissional</strong> (currículos no CRM).
            Benefícios usam tags de <strong>segmentação</strong> (marcadores do cidadão).
          </p>
        </div>
      </div>
      <p v-if="!podeGerenciar" class="text-xs text-gray-500 dark:text-slate-400 sm:max-w-[12rem]">
        Seu perfil pode visualizar os serviços; gestão exige permissão de talentos.
      </p>
    </div>

    <div v-if="carregando" class="flex items-center justify-center gap-2 py-16 text-gray-500">
      <Loader2 class="w-5 h-5 animate-spin" />
      Carregando resumo…
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
      <article
        v-for="secao in secoes"
        :key="secao.id"
        class="card flex flex-col hover:shadow-md transition-shadow border border-gray-200 dark:border-slate-700"
      >
        <div class="flex items-start gap-3">
          <div
            class="p-2.5 rounded-xl shrink-0"
            :style="{ backgroundColor: secao.cor + '18', color: secao.cor }"
          >
            <component :is="secao.icone" class="w-6 h-6" />
          </div>
          <div class="min-w-0">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-slate-100">{{ secao.titulo }}</h3>
            <p class="text-sm text-gray-600 dark:text-slate-400 mt-1 line-clamp-2">{{ secao.descricao }}</p>
          </div>
        </div>

        <dl class="grid grid-cols-2 gap-3 mt-5">
          <div
            v-for="m in secao.metricas"
            :key="m.label"
            class="rounded-lg bg-gray-50 dark:bg-slate-800/80 px-3 py-2"
          >
            <dt class="text-xs text-gray-500 dark:text-slate-400">{{ m.label }}</dt>
            <dd class="text-xl font-bold text-gray-900 dark:text-slate-100 tabular-nums">{{ m.valor }}</dd>
          </div>
        </dl>

        <button
          type="button"
          class="mt-5 inline-flex items-center justify-center gap-2 w-full py-2.5 rounded-lg text-sm font-medium text-white transition-opacity hover:opacity-90"
          :style="{ backgroundColor: secao.cor }"
          @click="ir(secao.rota)"
        >
          Gerenciar
          <ArrowRight class="w-4 h-4" />
        </button>
      </article>
    </div>

    <div class="card bg-gray-50 dark:bg-slate-800/50 border-dashed">
      <div class="flex items-center gap-2 text-sm text-gray-600 dark:text-slate-400">
        <Users class="w-4 h-4" />
        Dica: cadastre tags do módulo <strong class="font-medium text-gray-800 dark:text-slate-200">Serviços</strong>
        em Configurações → Classificações e use-as nos currículos do CRM.
      </div>
    </div>
  </div>
</template>
